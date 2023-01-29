#!/usr/bin/env python3
"""
Check BSON/JSON/YAML configuration files for errors.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        data = config_mod.Data()
        error = 0

        types = config_mod.Data.TYPES
        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                print(f"{path}: Cannot find file", file=sys.stderr)
                error = 1
                continue

            file_type = types.get(path.suffix)
            if file_type in ('bson', 'json', 'yaml'):
                print(f'Checking "{path}" {file_type.upper()} file...')
                try:
                    data.read(path, check=True)
                except config_mod.ReadConfigError as exception:
                    print(f"{path}: {exception}", file=sys.stderr)
                    error = 1

        return error


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
