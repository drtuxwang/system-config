#!/usr/bin/env python3
"""
Find file or directory.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import re
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDirectories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def getPattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Find file or directory.')

        parser.add_argument('pattern', nargs=1, help='Regular expression.')
        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory to search.')

        self._args = parser.parse_args(args)


class Finder:

    def __init__(self, options):
        self._options = options
        try:
            self._ispattern = re.compile(options.getPattern())
        except re.error:
            raise SystemExit(sys.argv[0] + ': Invalid regular expression "' +
                             options.getPattern() + '".')

    def _find(self, files):
        for file in sorted(files):
            if os.path.isdir(file) and not os.path.islink(file):
                try:
                    self._find([os.path.join(file, x) for x in os.listdir(file)])
                except PermissionError:
                    raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" directory.')

            elif self._ispattern.search(file):
                print(file)

    def run(self):
        self._find(self._options.getDirectories())


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Finder(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
