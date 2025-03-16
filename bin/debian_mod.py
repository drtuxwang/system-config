#!/usr/bin/env python3
"""
Debian software repository handling module

Copyright GPL v2: 2015-2025 By Dr Colin Kong
"""

import bz2
import datetime
import gzip
import logging
import lzma
import os
import re
import socket
import sys
import time
import urllib.request
from pathlib import Path
from typing import Generator, List, Tuple

import pyzstd  # type: ignore

from command_mod import Command
from file_mod import FileUtil
from logging_mod import ColoredFormatter
from subtask_mod import Task

RELEASE = '2.0.0'
VERSION = 20250316

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class DebianDist:
    """
    This class handles Debian dist repository file
    """
    tmpdir = FileUtil.tmpdir(Path('.cache', 'debget'))
    wget = Command('wget', args=[
        '--timestamping',
        '--dns-timeout=1',
        '--connect-timeout=1',
        '--read-timeout=10',
    ], errors='stop')

    def __init__(self, path: Path) -> None:
        self._path = path.with_suffix('')
        self._repos = list(self._read_dist(path))

    def _read_dist(self, path: Path) -> Generator[Tuple, None, None]:
        """
        Read dist file and yield (path, url).
        """
        isjunk = re.compile('.*/dists/|binary-|/Packages.*')
        n = 0
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    url = line.rstrip()
                    if url and not url.startswith('#'):
                        if '/dists/' not in url or Path(url).name not in (
                            'Packages.xz',
                            'Packages.bz2',
                            'Packages.gz',
                        ):
                            raise SystemExit(
                                f'{sys.argv[0]}: Invalid "{url}" URL.',
                            )
                        n += 1
                        file = f"{isjunk.sub('', url).replace('/', '_')}.zst"
                        yield Path(self._path, f'{n:02d}_{file}'), url
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" distribution file.',
            ) from exception

    @staticmethod
    def _read_packages(path: Path) -> List[str]:
        """
        Read and uncompress packages file
        """
        try:
            data = path.read_bytes()
            suffix = path.suffix
            if suffix == '.zst':
                data = pyzstd.decompress(data)  # pylint: disable=no-member
            elif suffix == '.xz':
                data = lzma.decompress(data)
            elif suffix == '.bz2':
                data = bz2.decompress(data)
            elif suffix == '.gz':
                data = gzip.decompress(data)
        except (lzma.LZMAError, gzip.BadGzipFile, OSError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.'
            ) from exception

        return data.decode(errors='replace').splitlines()

    def _remove(self) -> None:
        for path in Path(self.tmpdir).glob('Packages*'):
            try:
                path.unlink()
            except OSError:
                pass

    def _fetch_packages(self, url: str) -> bytes:
        """
        Fetch and uncompress packages file
        """
        self._remove()
        path = Path(self.tmpdir, Path(url).name)
        task = Task(self.wget.get_cmdline() + ['-O', path, url])
        task.run()
        if task.get_exitcode():
            self._remove()
            raise SystemExit(
                f'{sys.argv[0]}: Cannot fetch "{url}" file.'
            )

        try:
            data = path.read_bytes()
            suffix = path.suffix
            if suffix == '.xz':
                data = lzma.decompress(data)
            elif suffix == '.bz2':
                data = bz2.decompress(data)
            elif suffix == '.gz':
                data = gzip.decompress(data)
        except (lzma.LZMAError, gzip.BadGzipFile, OSError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot uncompress "{path}" file.'
            ) from exception
        self._remove()
        return data

    def _update_packages(self, path: Path, url: str) -> None:
        """
        Download updated Packages file.
        """
        for _ in range(8):  # Workaround some mirrors down
            try:
                with urllib.request.urlopen(url, timeout=0.2) as conn:
                    url_time = time.mktime(time.strptime(
                        conn.info().get('Last-Modified'),
                        '%a, %d %b %Y %H:%M:%S %Z',
                    ))
                break
            except (socket.timeout, urllib.error.URLError):
                return
        if path.is_file() and url_time <= path.stat().st_mtime:
            return
        if path.is_file():
            old_utc = datetime.datetime.fromtimestamp(path.stat().st_mtime)
            logger.warning(
                "[%s] packages metadata stored is out of date",
                old_utc.strftime('%Y-%m-%dT%H:%M:%S%z'),
            )
        new_utc = datetime.datetime.fromtimestamp(url_time)
        logger.info(
            "[%s] packages metadata new file data fetching",
            new_utc.strftime('%Y-%m-%dT%H:%M:%S%z'),
        )
        # Fix "\n " continuation and Filename:
        data = self._fetch_packages(url).replace(b'\n ', b' ').replace(
            b'Filename: ',
            f"Filename: {url[:url.find('/dists/') + 1]}".encode()
        )

        logger.info('Creating "%s" packages file.', path)
        path_new = Path(f'{path}.part')
        try:
            path_new.write_bytes(pyzstd.compress(data, 11))
            os.utime(path_new, (url_time, url_time))
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

    def get(self) -> Generator[str, None, None]:
        """
        Yield line from Packages files.
        """
        for path, _ in self._repos:
            yield from self._read_packages(path)

    def get_keys(self) -> dict:
        """
        Return dictionary of package keys.
        """
        data = {}
        package = {}
        key = None
        for path, _ in self._repos:
            for line in self._read_packages(path):
                if line:
                    key, value = line.split(': ', 1)
                    package[key] = value
                else:
                    data[
                        f"{package['Package']}:{package['Architecture']}"
                    ] = package
                    package = {}
        return data

    def update(self) -> None:
        """
        Download updated Packages files defined in dist file.
        """
        logger.info('Checking "%s" distribution packages cache.', self._path)
        if not self._path.is_dir():
            self._path.mkdir()
        for path, url in self._repos:
            self._update_packages(path, url)


if __name__ == '__main__':
    if sys.argv[-1] in ('-v', '-V', '-version', '--version'):
        print(f"Software repository handling module {RELEASE} ({VERSION})")
    else:
        help(__name__)
