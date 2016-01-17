#!/usr/bin/env python3
"""
Find zero sized files.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Find zero sized files.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory to search.')

        self._args = parser.parse_args(args)


class Findzero(object):
    """
    Find zero class
    """

    def __init__(self, options):
        self._findzero(options.get_directories())

    def _findzero(self, files):
        for file in sorted(files):
            if os.path.isdir(file):
                try:
                    self._findzero([os.path.join(file, x) for x in os.listdir(file)])
                except PermissionError:
                    pass
            elif syslib.FileStat(file).get_size() == 0:
                print(file)


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
            Findzero(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
