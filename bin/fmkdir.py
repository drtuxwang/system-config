#!/usr/bin/env python3
"""
Create a single lower case directory.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._directory = ''
        self.parse(sys.argv)

    def get_directory(self) -> str:
        """
        Return directory.
        """
        return os.path.expandvars(self._directory)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Create a single lower case directory",
        )
        parser.add_argument(
            'words',
            nargs='+',
            metavar='word',
            help="Part of directory name.",
        )

        words = parser.parse_args(args).words

        self._directory = '-'.join(words).lower()

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
        path = Path(Options().get_directory())

        if not path.is_dir():
            print(f'Creating "{path}"...')
            try:
                path.mkdir(parents=True)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create directory.',
                ) from exception

        return 0


if '--pydoc' in sys.argv:
    help(__name__)
else:
    Main()
