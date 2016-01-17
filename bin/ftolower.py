#!/usr/bin/env python3
"""
Convert filename to lowercase.
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

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Convert filename to lowercase.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to change.')

        self._args = parser.parse_args(args)


class ToLower(object):
    """
    To lowercase file class
    """

    def __init__(self, options):
        for file in options.get_files():
            if not os.path.isfile(file):
                if not os.path.isdir(file):
                    raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            if os.sep not in file:
                newfile = file.lower()
            elif file.endswith(os.sep):
                newfile = os.path.join(os.path.dirname(file), os.path.basename(file[:-1]).lower())
            else:
                newfile = os.path.join(os.path.dirname(file), os.path.basename(file).lower())
            if newfile != file:
                print('Converting filename "' + file + '" to lowercase...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename over existing "' + newfile + '" file.')
                try:
                    os.rename(file, newfile)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename "' + file + '" file to "' + newfile + '".')


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
            ToLower(options)
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
