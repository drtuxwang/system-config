#!/usr/bin/env python3
"""
Replace symbolic link to files with copies.
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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Replace symbolic link to files with copies.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Symbolic link to file.",
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
    def _copy(file: str, target: str) -> None:
        try:
            os.remove(file)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot remove "{file}" link.',
            ) from exception

        try:
            shutil.copy2(target, file)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot copy "{target}" file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.islink(file):
                target = os.path.realpath(file)
                if os.path.isfile(target):
                    print("Copy file:", file, '->', target)
                    self._copy(file, target)
                elif not os.path.isdir(target):
                    print("Null link:", file, '->', os.readlink(file))
            elif not os.path.exists(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" file.',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
