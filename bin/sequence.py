#!/usr/bin/env python3
"""
Generate sequence of numbers option with optional commas
"""

import argparse
import itertools
import signal
import sys
from typing import Generator, List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_commas(self) -> Generator[str, None, None]:
        """
        Comma generator.
        """
        if self._args.alldays or self._args.weekdays and self._args.weekends:
            commas = [' ', ' ', ' ', ' ', ',', ' ', ',']
        elif self._args.weekdays:
            commas = [' ', ' ', ' ', ' ', ',']
        elif self._args.weekends:
            commas = [' ', ',']
        else:
            commas = [' ']

        for comma in itertools.cycle(commas):
            yield comma

    def get_numbers(self) -> Generator[str, None, None]:
        """
        Number generator.
        """
        for number in range(self._args.first[0], self._args.last[0]+1):
            yield str(number)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Dump the first and last few bytes of a binary file.",
        )

        parser.add_argument(
            '-a',
            dest='alldays',
            action='store_true',
            help="Add comma every 5 and 2 numbers",
        )
        parser.add_argument(
            '-d',
            dest='weekdays',
            action='store_true',
            help="Add comma every 5 numbers",
        )
        parser.add_argument(
            '-e',
            dest='weekends',
            action='store_true',
            help="Add comma every 2 numbers",
        )
        parser.add_argument(
            'first',
            type=int,
            nargs=1,
            help="First number.",
        )
        parser.add_argument(
            'last',
            type=int,
            nargs=1,
            help="Last number.",
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

    @staticmethod
    def run() -> int:
        """
        Generate list
        """
        options = Options()

        for number, comma in zip(options.get_numbers(), options.get_commas()):
            print(number, comma, sep='', end='')
        print()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
