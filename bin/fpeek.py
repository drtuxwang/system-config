#!/usr/bin/env python3
"""
Dump the first and last few bytes of a binary file.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_all_flag(self):
        """
        Return all flag.
        """
        return self._args.all_flag

    def get_ascii_flag(self):
        """
        Return ascii flag.
        """
        return self._args.ascii_flag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Dump the first and last few bytes of a binary file.')

        parser.add_argument('-a', dest='all_flag', action='store_true',
                            help='Show contents of the whole file.')
        parser.add_argument('-c', dest='ascii_flag', action='store_true',
                            help='Show contents as ASCII characters.')

        parser.add_argument('files', nargs=1, metavar='file', help='File to view.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _format(options, data):
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

    def run(self):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            try:
                with open(file, 'rb') as ifile:
                    print('\nFile:', file)
                    file_stat = file_mod.FileStat(file)
                    if options.get_all_flag() or file_stat.get_size() < 128:
                        for position in range(1, file_stat.get_size() + 1, 16):
                            print('{0:07d}{1:s}'.format(
                                position, self._format(options, ifile.read(16))))
                    else:
                        for position in range(1, 65, 16):
                            print('{0:07d}{1:s}'.format(
                                position, self._format(options, ifile.read(16))))
                        print('...')
                        ifile.seek(file_stat.get_size() - 64)
                        for position in range(
                                file_stat.get_size() - 63, file_stat.get_size() + 1, 16):
                            print('{0:07d}{1:s}'.format(
                                position, self._format(options, ifile.read(16))))
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
