#!/usr/bin/env python3
"""
Remove files or directories.
"""

import argparse
import glob
import os
import shutil
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

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Remove files or directories.')

        parser.add_argument('-R', dest='recursiveFlag', action='store_true',
                            help='Remove directories recursively.')

        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Remove(object):
    """
    Remove class
    """

    def __init__(self, options):
        self._options = options
        for file in options.get_files():
            if os.path.isfile(file):
                self._rmfile(file)
            elif os.path.isdir(file):
                self._rmdir(file)
            else:
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file or directory.')

    def _rmfile(self, file):
        print('Removing "' + file + '" file...')
        try:
            os.remove(file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot remove "' + file + '" file.')

    def _rmdir(self, directory):
        if self._options.get_recursive_flag():
            print('Removing "' + directory + '" directory recursively...')
            try:
                shutil.rmtree(directory)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot remove "' + directory + '" directory.')
        else:
            print(sys.argv[0] + ': Ignoring "' + directory + '" directory.')


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
            Remove(options)
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
