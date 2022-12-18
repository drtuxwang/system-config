#!/usr/bin/env python3
"""
Generate random integer from range.
"""

import argparse
import glob
import os
import random
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

    def get_values(self) -> List[str]:
        """
        Return list of values.
        """
        return self._args.values

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Generate random integer from range.",
        )

        parser.add_argument(
            'values',
            nargs='+',
            metavar='value',
            help="Maximum integer value.",
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
        sys.exit(0)

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
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
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

        values = options.get_values()

        for value in values:
            try:
                print(random.randint(1, int(value)))
            except ValueError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Not an integer: {value}',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
