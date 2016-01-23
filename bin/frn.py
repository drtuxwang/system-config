#!/usr/bin/env python3
"""
Rename file/directory by replacing some characters.
"""

import argparse
import glob
import os
import re
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

    def get_pattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def get_replacement(self):
        """
        Return replacement.
        """
        return self._args.replacement[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Rename file/directory by replacing some characters.')

        parser.add_argument('pattern', nargs=1, help='Regular expression.')
        parser.add_argument('replacement', nargs=1, help='Replacement for matches.')
        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Rename(object):
    """
    Rename class
    """

    def __init__(self, options):
        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error:
            raise SystemExit(sys.argv[0] + ': Invalid regular expression "' +
                             options.get_pattern() + '".')

        self._replacement = options.get_replacement()
        self._files = options.get_files()

    def run(self):
        """
        Start change
        """
        for file in self._files:
            if os.sep in file:
                newfile = os.path.join(os.path.dirname(file), self._is_match.sub(
                    self._replacement, os.path.basename(file)))
            else:
                newfile = self._is_match.sub(self._replacement, file)
            if newfile != file:
                print('Renaming "' + file + '" to "' + newfile + '"...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename over existing "' + newfile + '" file.')
                try:
                    os.rename(file, newfile)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot rename to "' + newfile + '" file.')


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
            Rename(options).run()
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
