#!/usr/bin/env python3
"""
Count number of lines and maximum columns used in file.
"""

import argparse
import glob
import os
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Count number of lines and maximum columns used in file.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to examine.')

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
    def run():
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.isfile(file):
                if not os.path.isfile(file):
                    raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
                nlines = 0
                maxcols = 0
                try:
                    with open(file, errors='replace') as ifile:
                        for line in ifile:
                            nlines += 1
                            ncols = len(line.rstrip('\r\n'))
                            if ncols > maxcols:
                                maxcols = ncols
                                lline = nlines
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
                except UnicodeDecodeError:  # Non text file
                    continue
                print('{0:s}: {1:d} lines (max length of {2:d} on line {3:d})'.format(
                    file, nlines, maxcols, lline))

if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
