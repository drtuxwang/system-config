#!/usr/bin/env python3
"""
Convert filename to uppercase.
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
            description="Convert filename to uppercase.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to change.",
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
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" file.')
            if os.sep not in file:
                newfile = file.upper()
            elif file.endswith(os.sep):
                newfile = os.path.join(
                    os.path.dirname(file), os.path.basename(file[:-1]).upper())
            else:
                newfile = os.path.join(
                    os.path.dirname(file), os.path.basename(file).upper())
            if newfile != file:
                print(f'Converting filename "{file}" to uppercase...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot rename over existing '
                        f'"{newfile}" file.',
                    )
                try:
                    shutil.move(file, newfile)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot rename '
                        f'"{file}" file to "{newfile}".',
                    ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
