#!/usr/bin/env python3
"""
Find file or directory.
"""

import argparse
import glob
import re
import os
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

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def get_pattern(self) -> str:
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description='Find file or directory.')

        parser.add_argument(
            'pattern',
            nargs=1,
            help='Regular expression.'
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory to search.'
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

    def _find(self, files: List[str]) -> None:
        for file in sorted(files):
            if os.path.isdir(file) and not os.path.islink(file):
                try:
                    self._find([
                        os.path.join(file, x)
                        for x in os.listdir(file)
                    ])
                except PermissionError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot open "' + file +
                        '" directory.'
                    ) from exception

            elif self._ispattern.search(file):
                print(file)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        try:
            self._ispattern = re.compile(options.get_pattern())
        except re.error as exception:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' +
                options.get_pattern() + '".'
            ) from exception

        self._find(options.get_directories())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
