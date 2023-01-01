#!/usr/bin/env python3
"""
Download Debian packages list files.
"""

import argparse
import datetime
import functools
import glob
import json
import logging
import os
import signal
import socket
import sys
import time
import urllib.request
from pathlib import Path
from typing import List

import pyzstd

import command_mod
import file_mod
import logging_mod
import subtask_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_distribution_files(self) -> List[str]:
        """
        Return list of distribution files.
        """
        return self._args.distribution_files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Download Debian packages list files.",
        )

        parser.add_argument(
            'distribution_files',
            nargs='+',
            metavar='distribution.dist',
            help="File containing Debian package URLs.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    def config(self) -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

        self.tmpdir = file_mod.FileUtil.tmpdir(Path('.cache', 'debget'))

    @staticmethod
    def _get_urls(path: Path) -> List[str]:
        urls = []
        try:
            with path.open(encoding='utf-8', errors='replace') as ifile:
                for url in ifile:
                    url = url.rstrip()
                    if url and not url.startswith('#'):
                        if (
                            not url.startswith(('http://', 'https://')) or
                            Path(url).name not in (
                                'Packages.xz',
                                'Packages.bz2',
                                'Packages.gz',
                            )
                        ):
                            raise SystemExit(
                                f'{sys.argv[0]}: Invalid "{url}" URL.',
                            )
                        urls.append(url)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" distribution file.',
            ) from exception
        return urls

    def _remove(self) -> None:
        for path in Path(self.tmpdir).glob('Packages*'):
            try:
                path.unlink()
            except OSError:
                pass

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _get_cmdline(name: str) -> List[str]:
        command = command_mod.Command(name, errors='stop')

        return command.get_cmdline()

    @classmethod
    def _unpack(cls, path: Path) -> None:
        if path.suffix == '.xz':
            cmdline = cls._get_cmdline('unxz') + [str(path)]
        elif path.suffix == '.bz2':
            cmdline = cls._get_cmdline('bzip2') + ['-d', str(path)]
        elif path.suffix == '.gz':
            cmdline = cls._get_cmdline('gzip') + ['-d', str(path)]
        else:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot unpack "{path}" package file.',
            )
        subtask_mod.Task(cmdline).run(directory=path.parent)

    @staticmethod
    def _show_times(old_utime: float, new_utime: float) -> None:
        new_utc = datetime.datetime.fromtimestamp(new_utime)
        if old_utime:
            old_utc = datetime.datetime.fromtimestamp(old_utime)
            logger.warning(
                "[%s] packages metadata stored is out of date",
                old_utc.strftime('%Y-%m-%d-%H:%M:%S'),
            )
        logger.info(
            "[%s] packages metadata new file data fetching",
            new_utc.strftime('%Y-%m-%d-%H:%M:%S'),
        )

    def _get_packages(
        self,
        data: dict,
        wget: command_mod.Command,
        url: str,
    ) -> dict:
        for _ in range(3):
            try:
                with urllib.request.urlopen(url, timeout=1) as conn:
                    url_time = time.mktime(time.strptime(
                        conn.info().get('Last-Modified'),
                        '%a, %d %b %Y %H:%M:%S %Z',
                    ))
                break
            except (socket.timeout, urllib.error.URLError):
                pass
        else:
            raise SystemExit(f"Error: Cannot fetch URL: {url}")

        if url_time > data['time']:
            self._show_times(data['time'], url_time)
            archive_path = Path(self.tmpdir, Path(url).name)
            self._remove()
            task = subtask_mod.Task(
                wget.get_cmdline() + ['-O', str(archive_path), url]
            )
            for _ in range(3):
                task.run()
                if task.get_exitcode() == 0:
                    break
                self._remove()
            else:
                print("  [ERROR (", task.get_exitcode, ")]", url)
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            self._unpack(archive_path)
            site = url[:url.find('/dists/') + 1]

            lines = []
            path = Path(archive_path.parent, archive_path.stem)
            try:
                with path.open(encoding='utf-8', errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('Filename: '):
                            lines.append(line.rstrip('\r\n').replace(
                                'Filename: ', f'Filename: {site}', 1))
                        else:
                            lines.append(line.rstrip('\r\n'))
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "Packages" packages file.',
                ) from exception
            self._remove()
            data = {'time': url_time, 'text': lines}

        return data

    @staticmethod
    def _read_data(path: Path) -> dict:
        try:
            data = json.loads(pyzstd.decompress(  # pylint: disable=no-member
                 path.read_bytes()
            ))
        except json.decoder.JSONDecodeError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Corrupt "{path}" file.',
            ) from exception
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.'
            ) from exception

        return data

    @staticmethod
    def _write_data(path: Path, data: dict) -> None:
        logger.info('Creating "%s" packages file.', path)
        path_new = Path(f'{path}.part')
        try:
            path_new.write_bytes(pyzstd.compress(  # pylint: disable=no-member
                json.dumps(data, ensure_ascii=False).encode(),
                11,
            ))
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{path_new}" file.',
            ) from exception
        try:
            path_new.replace(path)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{path}" file.',
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        os.umask(0o022)

        options = Options()

        wget = command_mod.Command(
            'wget',
            args=['--timestamping', '--connect-timeout=1'],
            errors='stop'
        )

        for dist_path in [Path(x) for x in options.get_distribution_files()]:
            if dist_path.suffix == '.dist':
                logger.info('Checking "%s" distribution file.', dist_path)

                path = dist_path.with_suffix('.json.zstd')
                data = (
                    self._read_data(path)
                    if path.is_file()
                    else {'data': {}, 'urls': []}
                )
                old_time = max(
                    [0] + [x['time'] for x in data['data'].values()]
                )

                urls = self._get_urls(dist_path)
                for url in urls:
                    data['data'][url] = self._get_packages(
                        data['data'].get(url, {'time': 0}),
                        wget,
                        url
                    )

                new_time = max(x['time'] for x in data['data'].values())
                if new_time > old_time or data['urls'] != urls:
                    data['urls'] = urls
                    self._write_data(path, data)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
