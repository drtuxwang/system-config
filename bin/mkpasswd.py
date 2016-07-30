#!/usr/bin/env python3
"""
Create secure random password.
"""

import argparse
import glob
import os
import random
import signal
import string
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_symbols_flag(self):
        """
        Return symbols flag.
        """
        return self._args.symbols_flag

    def get_length(self):
        """
        Return length.
        """
        return self._args.length[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create secure random password.')

        parser.add_argument(
            '-s',
            dest='symbols_flag',
            action='store_true',
            help='Select additional symbols.'
        )
        parser.add_argument(
            'length',
            nargs=1,
            type=int,
            help='Password length.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.length[0] < 0:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'password length.'
            )


class Main(object):
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

        chars = string.ascii_letters + string.digits
        if options.get_symbols_flag():
            chars += '!@#$%^&*()'

        print(''.join(random.choice(chars) for i in range(
            options.get_length())))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
