#!/usr/bin/env python3
"""
Check PATH and return correct settings.
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

        self._path = os.environ['PATH']

    def get_path(self):
        """
        Return search path.
        """
        return self._path

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Check PATH and return correct settings.')

        self._args = parser.parse_args(args)


class Chkpath(object):
    """
    Check path class
    """

    def __init__(self, options):
        path = []
        print()
        for directory in options.get_path().split(os.pathsep):
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
            Chkpath(options)
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
