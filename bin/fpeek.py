#!/usr/bin/env python3
"""
Dump the first and last few bytes of a binary file.
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

    def get_all_flag(self):
        """
        Return all flag.
        """
        return self._args.allFlag

    def get_ascii_flag(self):
        """
        Return ascii flag.
        """
        return self._args.asciiFlag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Dump the first and last few bytes of a binary file.')

        parser.add_argument('-a', dest='allFlag', action='store_true',
                            help='Show contents of the whole file.')
        parser.add_argument('-c', dest='asciiFlag', action='store_true',
                            help='Show contents as ASCII characters.')

        parser.add_argument('files', nargs=1, metavar='file', help='File to view.')

        self._args = parser.parse_args(args)


class Dump(object):
    """
    Dump class
    """

    def __init__(self, options):
        for file in options.get_files():
            try:
                with open(file, 'rb') as ifile:
                    print('\nFile:', file)
                    fileStat = syslib.FileStat(file)
                    if options.get_all_flag() or fileStat.get_size() < 128:
                        for position in range(1, fileStat.get_size() + 1, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
                    else:
                        for position in range(1, 65, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
                        print('...')
                        ifile.seek(fileStat.get_size() - 64)
                        for position in range(
                                fileStat.get_size() - 63, fileStat.get_size() + 1, 16):
                            print('{0:07d}{1:s}'.format(position,
                                  self._format(options, ifile.read(16))))
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

    def _format(self, options, data):
        if options.get_ascii_flag():
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
            Dump(options)
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
