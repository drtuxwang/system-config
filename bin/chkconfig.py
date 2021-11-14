#!/usr/bin/env python3
"""
Check BSON/JSON/YAML configuration files for errors.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import config_mod


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
            description="Check BSON/JSON/YAML configuration files for errors.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to check.",
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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        data = config_mod.Data()
        error = 0

        for file in options.get_files():
            if not os.path.isfile(file):
                print(f"{file}: Cannot find file")
                error = 1
            elif file.endswith(('.json', 'yaml', 'yml', '.bson')):
                try:
                    data.read(file, check=True)
                except config_mod.ReadConfigError as exception:
                    print(f"{file}: {exception}")
                    error = 1

        return error


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
