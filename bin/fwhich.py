#!/usr/bin/env python3
"""
Locate a program file.
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

        if os.name == 'nt':
            self._extensions = os.environ['PATHEXT'].lower().split(os.pathsep) + ['.py', '']
        else:
            self._extensions = ['']

    def get_all_flag(self):
        """
        Return all flag.
        """
        return self._args.allFlag

    def get_extensions(self):
        """
        Return list of executable extensions.
        """
        return self._extensions

    def get_programs(self):
        """
        Return list of programs.
        """
        return self._args.programs

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Locate a program file.')

        parser.add_argument('-a', dest='allFlag', action='store_true',
                            help='Show the location of all occurances.')

        parser.add_argument('programs', nargs='+', metavar='program', help='Command to search.')

        self._args = parser.parse_args(args)


class Which(object):
    """
    Main class
    """

    def __init__(self, options):
        self._options = options
        self._path = os.environ['PATH']
        for program in options.get_programs():
            self._locate(program)

    def _locate(self, program):
        found = []
        for directory in self._path.split(os.pathsep):
            if os.path.isdir(directory):
                for extension in self._options.get_extensions():
                    file = os.path.join(directory, program) + extension
                    if file not in found and os.path.isfile(file):
                        found.append(file)
                        print(file)
                        if not self._options.get_all_flag():
                            return

        if not found:
            print(program, 'not in:')
            for directory in self._path.split(os.pathsep):
                print(' ', directory)
        raise SystemExit(1)


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
            Which(options)
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
