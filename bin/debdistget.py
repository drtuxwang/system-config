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
import shutil
import signal
import sys
import time
import urllib.request
from typing import List

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
            description='Download Debian packages list files.',
        )

        parser.add_argument(
            'distribution_files',
            nargs='+',
            metavar='distribution.dist',
            help='File containing Debian package URLs.'
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
            sys.exit(exception)

    def config(self) -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

        self.tmpdir = file_mod.FileUtil.tmpdir(
            os.path.join('.cache', 'debdistget')
        )

    @staticmethod
    def _get_urls(distribution_file: str) -> List[str]:
        urls = []
        try:
            with open(distribution_file, errors='replace') as ifile:
                for url in ifile:
                    url = url.rstrip()
                    if url and not url.startswith('#'):
                        if (not url.startswith('http://') or
                                os.path.basename(url) not in (
                                    'Packages.xz', 'Packages.bz2',
                                    'Packages.gz')):
                            raise SystemExit(
                                sys.argv[0] + ': Invalid "' + url + '" URL.')
                        urls.append(url)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + distribution_file +
                '" distribution file.'
            ) from exception
        return urls

    def _remove(self) -> None:
        for file in glob.glob(os.path.join(self.tmpdir, 'Packages*')):
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _get_cmdline(name: str) -> List[str]:
        command = command_mod.Command(name, errors='stop')

        return command.get_cmdline()

    @classmethod
    def _unpack(cls, file: str) -> None:
        directory = os.path.dirname(file)
        if file.endswith('.xz'):
            cmdline = cls._get_cmdline('unxz') + [file]
        elif file.endswith('.bz2'):
            cmdline = cls._get_cmdline('bzip2') + ['-d', file]
        elif file.endswith('.gz'):
            cmdline = cls._get_cmdline('gzip') + ['-d', file]
        else:
            raise SystemExit(
                sys.argv[0] + ': Cannot unpack "' + file + '" package file.')
        subtask_mod.Task(cmdline).run(directory=directory)

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
        try:
            with urllib.request.urlopen(url) as conn:
                url_time = time.mktime(time.strptime(
                    conn.info().get('Last-Modified'),
                    '%a, %d %b %Y %H:%M:%S %Z',
                ))
        except Exception as exception:
            raise SystemExit(
                "Error: Cannot fetch URL: " + url
            ) from exception

        if url_time > data['time']:
            self._show_times(data['time'], url_time)
            archive = os.path.join(self.tmpdir, os.path.basename(url))
            self._remove()
            task = subtask_mod.Task(wget.get_cmdline() + ['-O', archive, url])
            task.run()
            if task.get_exitcode() != 0:
                print("  [ERROR (", task.get_exitcode, ")]", url)
                self._remove()
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            self._unpack(archive)
            site = url[:url.find('/dists/') + 1]

            lines = []
            file = archive.rsplit('.', 1)[0]
            try:
                with open(file, errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('Filename: '):
                            lines.append(line.rstrip('\r\n').replace(
                                'Filename: ', 'Filename: ' + site, 1))
                        else:
                            lines.append(line.rstrip('\r\n'))
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "Packages" packages file.'
                ) from exception
            self._remove()
            data = {'time': url_time, 'text': lines}

        return data

    @staticmethod
    def _read_data(file: str) -> dict:
        try:
            with open(file) as ifile:
                data = json.load(ifile)
        except json.decoder.JSONDecodeError as exception:
            raise SystemExit(
                sys.argv[0] + ': Corrupt "' + file + '" json file.'
            ) from exception
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            ) from exception

        return data

    @staticmethod
    def _write_data(file: str, data: dict) -> None:
        logger.info('Creating "%s" packages file.', file)
        try:
            with open(file + '.part', 'w', newline='\n') as ofile:
                print(json.dumps(data, ensure_ascii=False), file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '.part" file.'
            ) from exception
        try:
            shutil.move(file + '.part', file)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" file.'
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()

        wget = command_mod.Command(
            'wget',
            args=['--timestamping'],
            errors='stop'
        )

        for distribution_file in options.get_distribution_files():
            if distribution_file.endswith('.dist'):
                logger.info(
                    'Checking "%s" distribution file.',
                    distribution_file,
                )

                json_file = distribution_file[:-4] + 'json'
                if os.path.isfile(json_file):
                    distribution_data = self._read_data(json_file)
                else:
                    distribution_data = {
                        'data': {},
                        'urls': []
                    }
                old_time = max([0] + [
                    data['time']
                    for data in distribution_data['data'].values()
                ])

                urls = self._get_urls(distribution_file)
                for url in urls:
                    distribution_data['data'][url] = self._get_packages(
                        distribution_data['data'].get(url, {'time': 0}),
                        wget,
                        url
                    )

                new_time = max([
                    data['time']
                    for data in distribution_data['data'].values()
                ])
                if new_time > old_time or distribution_data['urls'] != urls:
                    distribution_data['urls'] = urls
                    self._write_data(json_file, distribution_data)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
