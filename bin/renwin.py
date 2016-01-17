#!/usr/bin/env python3
"""
Rename window title.
"""

import argparse
import glob
import os
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

        self._title = ' '.join(args[1:])

    def get_title(self):
        """
        Return title of files.
        """
        return self._title

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Rename window title.')

        parser.add_argument('words', nargs='+', metavar='word', help='A word.')

        self._args = parser.parse_args(args)


class Title(object):
    """
    Title class
    """

    def __init__(self, options):
        term = self._getterm()
        if term in ['xterm', 'xvt100']:
            sys.stdout.write('\033]0;' + options.get_title() + '\007')
        elif term.startswith('iris-ansi'):
            sys.stdout.write('\033P3.y' + options.get_title() + '\033\\')
            sys.stdout.write('\033P1.y' + options.get_title() + '\033\\')
        else:
            raise SystemExit(sys.argv[0] + ': Unsupported "' + term + '" terminal type.')

    def _getterm(self):
        term = 'Unkown'
        if 'TERM' in os.environ:
            term = os.environ['TERM']
        return term


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
            Title(options)
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
