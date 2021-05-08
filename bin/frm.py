#!/usr/bin/env python3
"""
Remove files or directories.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
from typing import List


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

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Remove files or directories.',
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Remove directories recursively.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
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
    def _rmfile(file: str) -> None:
        print('Removing "' + file + '" file...')
        try:
            os.remove(file)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot remove "' + file + '" file.'
            ) from exception

    def _rmdir(self, directory: str) -> None:
        if self._options.get_recursive_flag():
            print('Removing "' + directory + '" directory recursively...')
            try:
                shutil.rmtree(directory)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' +
                    directory + '" directory.'
                ) from exception
        else:
            print(sys.argv[0] + ': Ignoring "' + directory + '" directory.')

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        for file in self._options.get_files():
            if os.path.isfile(file):
                self._rmfile(file)
            elif os.path.isdir(file):
                self._rmdir(file)
            else:
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file +
                    '" file or directory.'
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
