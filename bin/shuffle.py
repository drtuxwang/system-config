#!/usr/bin/env python3
"""
Print arguments in random order.
"""

import argparse
import glob
import os
import random
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_words(self):
        """
        Return list of words.
        """
        return self._args.words

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Print arguments in random order.')

        parser.add_argument('words', nargs='+', metavar='word', help='A word.')

        self._args = parser.parse_args(args)


class Shuffle(object):
    """
    Shuffle class
    """

    def __init__(self, items):
        random.shuffle(items)
        for item in items:
            print(item)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Shuffle(options.get_words())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
