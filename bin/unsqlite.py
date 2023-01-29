#!/usr/bin/env python3
"""
Unpack a sqlite database file.
"""

import argparse
import os
import signal
import sqlite3
import sys
from pathlib import Path
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
            description="Unpack a sqlite database file.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive (default).",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.sqlite',
            help="Sqlite database file.",
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
    def _show(file: str) -> None:
        with sqlite3.connect(file) as conn:
            print(f"{file}:")
            try:
                for line in conn.iterdump():
                    print("   ", line)
            except sqlite3.DatabaseError as exception:
                raise SystemExit(f'{sys.argv[0]}: {exception}') from exception

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not Path(file).is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" database file.',
                )
            cls._show(file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
