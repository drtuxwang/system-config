#!/usr/bin/env python3
"""
Unicode sort lines of a file.
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

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Unicode sort lines of a file.')

        parser.add_argument('files', nargs=1, metavar='file',
                            help='File contents to sort.')

        self._args = parser.parse_args(args)


class Sort(object):
    """
    Sort class
    """

    def __init__(self, options):
        self._lines = []
        if len(options.get_files()):
            for file in options.get_files():
                try:
                    with open(file, errors='replace') as ifile:
                        for line in ifile:
                            line = line.rstrip('\r\n')
                            self._lines.append(line)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
        else:
            for line in sys.stdin:
                self._lines.append(line.rstrip('\r\n'))
        self._lines = sorted(self._lines)

    def print(self):
        for line in self._lines:
            print(line)


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
            Sort(options).print()
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
