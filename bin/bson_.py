#!/usr/bin/env python3
"""
Convert BSON/JSON/YAML to BSON file.
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
            description="Convert BSON/JSON/YAML to BSON file.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to convert.",
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
        data = config_mod.Data()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{file}" file.')
            if file.endswith(('.json', 'yaml', 'yml', '.bson')):
                try:
                    data.read(file)
                except config_mod.ReadConfigError as exception:
                    raise SystemExit(f"{file}: {exception}") from exception

                name, _ = os.path.splitext(file)
                bson_file = name + '.bson'
                print(f'Converting "{file}" to "{bson_file}"...')
                try:
                    data.write(bson_file)
                except config_mod.WriteConfigError as exception:
                    raise SystemExit(f"{file}: {exception}") from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
