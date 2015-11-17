#!/usr/bin/env python3
"""
Check PATH and return correct settings.
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

        self._path = os.environ['PATH']

    def getPath(self):
        """
        Return search path.
        """
        return self._path

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Check PATH and return correct settings.')

        self._args = parser.parse_args(args)


class Chkpath(syslib.Dump):

    def __init__(self, options):
        path = []
        print()
        for directory in options.getPath().split(os.pathsep):
            if directory:
                if not os.path.isdir(directory):
                    print(directory + ': fail')
                elif directory in path:
                    print(directory + ': repeat')
                else:
                    print(directory + ': ok')
                    path.append(directory)
        print('\nThe correct PATH should be:')
        print(os.pathsep.join(path))


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Chkpath(options)
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
