#!/usr/bin/env python3
"""
Dump the first and last few bytes of a binary file.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getAllFlag(self):
        """
        Return all flag.
        """
        return self._args.allFlag

    def getAsciiFlag(self):
        """
        Return ascii flag.
        """
        return self._args.asciiFlag

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Dump the first and last few bytes of a binary file.')

        parser.add_argument('-a', dest='allFlag', action='store_true',
                            help='Show contents of the whole file.')
        parser.add_argument('-c', dest='asciiFlag', action='store_true',
                            help='Show contents as ASCII characters.')

        parser.add_argument('files', nargs=1, metavar='file', help='File to view.')

        self._args = parser.parse_args(args)


class Dump(syslib.Dump):

    def __init__(self, options):
        for file in options.getFiles():
            try:
                with open(file, 'rb') as ifile:
                    print('\nFile:', file)
                    fileStat = syslib.FileStat(file)
                    if options.getAllFlag() or fileStat.getSize() < 128:
                        for position in range(1, fileStat.getSize() + 1, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
                    else:
                        for position in range(1, 65, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
                        print('...')
                        ifile.seek(fileStat.getSize() - 64)
                        for position in range(fileStat.getSize() - 63, fileStat.getSize() + 1, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

    def _format(self, options, data):
        if options.getAsciiFlag():
            line = ' '
            for byte in data:
                if byte > 31 and byte < 127:
                    line += '   ' + chr(byte)
                elif byte == 10:
                    line += r'  \n'
                elif byte == 13:
                    line += r'  \r'
                else:
                    line += ' ' + str(byte).zfill(3)
        else:
            line = ' '
            for byte in data:
                line += ' ' + str(byte).rjust(3)
        return line


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Dump(options)
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
