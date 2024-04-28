#!/usr/bin/env python3
"""
Display file status.
"""

import argparse
import os
import signal
import sys
from typing import List

from file_mod import FileStat


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_local_flag(self) -> bool:
        """
        Return local flag.
        """
        return self._args.local_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Display file status.")

        parser.add_argument(
            '-l',
            dest='local_flag',
            action='store_true',
            help="Show dates using local time zone.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File or directory.",
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        local_flag = options.get_local_flag()

        for file in options.get_files():
            file_stat = FileStat(file)
            print(f'"{file}".dev   = {file_stat.get_inode_device()}')
            print(f'"{file}".inode = {file_stat.get_inode_number()}')
            print(f'"{file}".nlink = {file_stat.get_number_links()}')
            print(f'"{file}".mode  = {oct(file_stat.get_mode())}')
            print(f'"{file}".uid   = {file_stat.get_userid()}')
            print(f'"{file}".gid   = {file_stat.get_groupid()}')
            print(f'"{file}".size  = {file_stat.get_size()}')
            if local_flag:
                print(f'"{file}".atime = {file_stat.get_atime_local()}')
                print(f'"{file}".mtime = {file_stat.get_mtime_local()}')
                print(f'"{file}".ctime = {file_stat.get_ctime_local()}')
            else:
                print(f'"{file}".atime = {file_stat.get_atime():.7f}')
                print(f'"{file}".mtime = {file_stat.get_mtime():.7f}')
                print(f'"{file}".ctime = {file_stat.get_ctime():.7f}')

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
