#!/usr/bin/env python3
"""
Output the last n lines of a file.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):

        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getLines(self):
        """
        Return number of lines.
        """
        return self._lines

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Output the last n lines of a file.')

        parser.add_argument('-n', nargs=1, type=int, dest='lines', default=[10], metavar='K',
                            help='Output last K lines. Use "-n +K" to output starting with Kth.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to search.')

        self._args = parser.parse_args(args)

        if ' -n +' in ' ' + ' '.join(args):
            self._lines = -self._args.lines[0]
        else:
            self._lines = self._args.lines[0]


class Tail:

    def __init__(self, options):
        if len(options.getFiles()) > 1:
            for file in options.getFiles():
                print('==>', file, '<==')
                self._file(options, file)
        elif len(options.getFiles()) == 1:
            self._file(options, options.getFiles()[0])
        else:
            self._pipe(options, sys.stdin)

    def _file(self, options, file):
        try:
            with open(file, errors='replace') as ifile:
                self._pipe(options, ifile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

    def _pipe(self, options, pipe):
        if options.getLines() > 0:
            buffer = []
            for line in pipe:
                line = line.rstrip('\r\n')
                buffer = (buffer + [line])[-options.getLines():]
            for line in buffer:
                try:
                    print(line)
                except IOError:
                    raise SystemExit(0)
        else:
            for i in range(-options.getLines() - 1):
                line = pipe.readline()
                if not line:
                    break
            for line in pipe:
                try:
                    print(line.rstrip('\r\n'))
                except IOError:
                    raise SystemExit(0)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Tail(options)
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
