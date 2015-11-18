#!/usr/bin/env python3
"""
Print lines matching a pattern.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getIgnoreCaseFlag(self):
        """
        Return ignore case flag.
        """
        return self._args.ignoreCaseFlag

    def getInvertFlag(self):
        """
        Return invert regular expression flag.
        """
        return self._args.invertFlag

    def getNumberFlag(self):
        """
        Return line number flag.
        """
        return self._args.numberFlag

    def getPattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Print lines matching a pattern.')

        parser.add_argument('-i', dest='ignoreCaseFlag', action='store_true',
                            help='Ignore case distinctions.')
        parser.add_argument('-n', dest='numberFlag', action='store_true',
                            help='Prefix each line of output with line number.')
        parser.add_argument('-v', dest='invertFlag', action='store_true',
                            help='Invert the sense of matching.')

        parser.add_argument('pattern', nargs=1, help='Regular expression.')
        parser.add_argument('files', nargs='+', metavar='file', help='File to search.')

        self._args = parser.parse_args(args)


class Grep:

    def __init__(self, options):
        try:
            if options.getIgnoreCaseFlag():
                self._isMatch = re.compile(options.getPattern(), re.IGNORECASE)
            else:
                self._isMatch = re.compile(options.getPattern())
        except re.error:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' + options.getPattern() + '".')
        if len(options.getFiles()) > 1:
            for file in options.getFiles():
                self._file(options, file, prefix=file + ':')
        elif len(options.getFiles()) == 1:
            self._file(options, options.getFiles()[0])
        else:
            self._pipe(options, sys.stdin)

    def _file(self, options, file, prefix=''):
        try:
            with open(file, errors='replace') as ifile:
                self._pipe(options, ifile, prefix)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

    def _pipe(self, options, pipe, prefix=''):
        number = 0
        if options.getInvertFlag():
            for line in pipe:
                line = line.rstrip('\r\n')
                number += 1
                if not self._isMatch.search(line):
                    if options.getNumberFlag():
                        line = str(number) + ':' + line
                    try:
                        print(prefix + line)
                    except IOError:
                        raise SystemExit(0)
        else:
            for line in pipe:
                line = line.rstrip('\r\n')
                number += 1
                if self._isMatch.search(line):
                    if options.getNumberFlag():
                        line = str(number) + ':' + line
                    try:
                        print(prefix + line)
                    except IOError:
                        raise SystemExit(0)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Grep(options)
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
