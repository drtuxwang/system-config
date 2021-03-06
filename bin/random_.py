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


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_values(self):
        """
        Return list of values.
        """
        return self._args.values

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Generate random integer from range.')

        parser.add_argument(
            'values',
            nargs='+',
            metavar='value',
            help='Maximum integer value.',
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    @staticmethod
    def config():
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
    def run():
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
                    sys.argv[0] + ': Not an integer: ' + value
                ) from exception


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
