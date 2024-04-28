#!/usr/bin/env python3
"""
Download http/https/ftp/file URLs.
"""

import argparse
import http
import json
import os
import signal
import socket
import sys
import time
import urllib.request
from pathlib import Path
from typing import List, Tuple

from config_mod import Config
from file_mod import FileStat
from task_mod import Tasks


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._config()
        self.parse(sys.argv)

    def get_urls(self) -> List[str]:
        """
        Return list of urls.
        """
        return self._args.urls

    @staticmethod
    def _config() -> None:
        if 'REQUESTS_CA_BUNDLE' not in os.environ:
            for file in (
                    # Debian/Ubuntu
                    '/etc/ssl/certs/ca-certificates.crt',
                    # RHEL/CentOS
                    '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'
            ):
                if Path(file).is_file():
                    os.environ['REQUESTS_CA_BUNDLE'] = file
                    break

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Download http/https/ftp/file URLs.",
        )

        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help="http/https/ftp/file URL.",
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

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _check_file(file: str, size: int, mtime: float) -> bool:
        """
        Check existing file and return True if already downloaded.
        """
        file_stat = FileStat(file)
        if file_stat.get_size() == size and file_stat.get_mtime() >= mtime:
            return True
        return False

    @staticmethod
    def _get_file_stat(
        url: str,
        conn: http.client.HTTPResponse,
    ) -> Tuple[str, int, float]:
        """
        url  = URL to download
        conn = http.client.HTTPResponse class object

        Returns (filename, size, time) tuple.
        """
        info = conn.info()

        try:
            mtime = time.mktime(time.strptime(
                info.get('Last-Modified'),
                '%a, %d %b %Y %H:%M:%S %Z',
            ))
        except TypeError:
            # For directories
            path = Path('index.html')
            if path.is_file():
                path = Path(f'index-{os.getpid()}.html')
            mtime = time.time()
        else:
            path = Path(Path(url).name)

        try:
            size = int(info.get('Content-Length'))
        except TypeError:
            size = -1

        return str(path), size, mtime

    @staticmethod
    def _check_resume(file: str, data: dict) -> str:
        """
        Return 'download', 'resume' or 'skip'
        """
        try:
            path = Path(f'{file}.part.json')
            json_data = json.loads(path.read_text(errors='replace'))
            host = json_data['fget']['lock']['host']
            pid = json_data['fget']['lock']['pid']

            if (
                host == socket.gethostname().split('.')[0].lower() and
                Tasks.factory().haspid(pid)
            ):
                return 'skip'
            if json_data['fget']['data'] == data:
                return 'resume'
        except (KeyError, OSError, ValueError):
            pass

        return 'download'

    @staticmethod
    def _write_resume(file: str, data: dict) -> None:
        json_data = {
            'fget': {
                'lock': {
                    'host': socket.gethostname().split('.')[0].lower(),
                    'pid': os.getpid()
                },
                'data': data
            }
        }

        try:
            with Path(f'{file}.part.json').open('w') as ofile:
                print(json.dumps(
                    json_data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except OSError:
            pass

    def _fetch(self, url: str) -> None:
        try:
            # pylint: disable=consider-using-with
            conn = urllib.request.urlopen(url)
            # pylint: enable=consider-using-with
        except Exception as exception:
            raise SystemExit(str(exception)) from exception

        file, size, mtime = self._get_file_stat(url, conn)
        if self._check_file(file, size, mtime):
            print(f"  => {file} [{size}/{size}]")
            return

        data = {'size': size, 'time': int(mtime)}
        check = self._check_resume(file, data)

        if check == 'skip':
            return
        if 'Accept-Ranges' in conn.info() and check == 'resume':
            tmpsize = Path(f'{file}.part').stat().st_size
            req = urllib.request.Request(url, headers={
                'Range': 'bytes='+str(tmpsize)+'-',
                'User-Agent': Config().get('user_agent'),
            })
            # pylint: disable=consider-using-with
            conn = urllib.request.urlopen(req)
            # pylint: enable=consider-using-with
            mode = 'ab'
        else:
            tmpsize = 0
            mode = 'wb'

        self._write_resume(file, data)

        try:
            with Path(f'{file}.part').open(mode) as ofile:
                while True:
                    chunk = conn.read(self._chunk_size)
                    if not chunk:
                        break
                    tmpsize += len(chunk)
                    ofile.write(chunk)
                    print(f"\r  => {file} [{tmpsize}/{size}]", end='')
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{file}" file.',
            ) from exception
        print()

        path_tmp = Path(f'{file}.part')
        os.utime(path_tmp, (mtime, mtime))
        try:
            path_tmp.replace(file)
            Path(f'{path_tmp}+.json')
        except OSError:
            pass

    def _get_url(self, url: str) -> None:
        print(url)

        try:
            self._fetch(url)
        except urllib.error.URLError as exception:
            reason = exception.reason
            if isinstance(reason, socket.gaierror):
                raise SystemExit(
                    f'{sys.argv[0]}: {reason.args[1]}.',
                ) from exception
            if 'Not Found' in str(reason):
                raise SystemExit(
                    f'{sys.argv[0]}: 404 Not Found.',
                ) from exception
            if 'Permission denied' in str(reason):
                raise SystemExit(
                    f'{sys.argv[0]}: 550 Permission denied.',
                ) from exception
            raise SystemExit(
               f'{sys.argv[0]}: {exception.args[0]}',
            ) from exception
        except ValueError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: {exception.args[0]}',
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._chunk_size = 131072
        self._urls = options.get_urls()

        for url in self._urls:
            self._get_url(url)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
