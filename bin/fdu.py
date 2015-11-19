#!/usr/bin/env python3
"""
Show file disk usage.
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

    def getSummaryFlag(self):
        """
        Return summary flag.
        """
        return self._args.summaryFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Show file disk usage.')

        parser.add_argument('-s', dest='summaryFlag', action='store_true',
                            help='Show summary only.')

        parser.add_argument('files', nargs='*', default=[os.curdir], metavar='file',
                            help='File or directory.')

        self._args = parser.parse_args(args)


class Diskusage:

    def __init__(self, options):
        for file in options.getFiles():
            if os.path.islink(file):
                print('{0:7d} {1:s}'.format(0, file))
            else:
                if os.path.isdir(file):
                    size = self._usage(options, file)
                    if options.getSummaryFlag():
                        print('{0:7d} {1:s}'.format(size, file))
                elif os.path.isfile(file):
                    size = int((syslib.FileStat(file).getSize() + 1023) / 1024)
                    print('{0:7d} {1:s}'.format(size, file))
                else:
                    print('{0:7d} {1:s}'.format(0, file))

    def _usage(self, options, directory):
        size = 0
        try:
            files = [os.path.join(directory, x) for x in os.listdir(directory)]
        except PermissionError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + directory + '" directory.')
        for file in sorted(files):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    size += self._usage(options, file)
                else:
                    size += int((syslib.FileStat(file).getSize() + 1023) / 1024)
        if not options.getSummaryFlag():
            print('{0:7d} {1:s}'.format(size, directory))
        return size


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Diskusage(options)
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
