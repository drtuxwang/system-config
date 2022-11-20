#!/usr/bin/env python3
"""
Display file status.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Display file status.")

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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            file_stat = file_mod.FileStat(file)
            print(f'"{file}".mode  =', oct(file_stat.get_mode()))
            print(f'"{file}".ino   =', file_stat.get_inode_number())
            print(f'"{file}".dev   =', file_stat.get_inode_device())
            print(f'"{file}".nlink =', file_stat.get_number_links())
            print(f'"{file}".uid   =', file_stat.get_userid())
            print(f'"{file}".gid   =', file_stat.get_groupid())
            print(f'"{file}".size  =', file_stat.get_size())
            print(f'"{file}".atime =', file_stat.get_time_access())
            print(f'"{file}".mtime =', file_stat.get_time())
            print(f'"{file}".ctime =', file_stat.get_time_change())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
