#!/usr/bin/env python3
"""
Rename window title.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._title = ' '.join(args[1:])

    def getTitle(self):
        """
        Return title of files.
        """
        return self._title

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Rename window title.')

        parser.add_argument('words', nargs='+', metavar='word', help='A word.')

        self._args = parser.parse_args(args)


class Title(syslib.Dump):

    def __init__(self, options):
        term = self._getterm()
        if term in ['xterm', 'xvt100']:
            sys.stdout.write('\033]0;' + options.getTitle() + '\007')
        elif term.startswith('iris-ansi'):
            sys.stdout.write('\033P3.y' + options.getTitle() + '\033\\')
            sys.stdout.write('\033P1.y' + options.getTitle() + '\033\\')
        else:
            raise SystemExit(sys.argv[0] + ': Unsupported "' + term + '" terminal type.')

    def _getterm(self):
        term = 'Unkown'
        if 'TERM' in os.environ:
            term = os.environ['TERM']
        return term


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
