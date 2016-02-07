#!/usr/bin/env python3
"""
Chop up a file into chunks.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_file(self):
        """
        Return file.
        """
        return self._args.file[0]

    def get_max_size(self):
        """
        Return max size of file part.
        """
        return self._max_size

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Chop up a file into chunks.')

        parser.add_argument('file', nargs=1, help='File to break up.')
        parser.add_argument('size', nargs=1, metavar='bytes|nMB',
                            help='Maximum chunk size to break up.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        try:
            size = self._args.size[0]
            if size.endswith('MB'):
                self._max_size = int(size[:-2]) * 1024**2
            else:
                self._max_size = int(size)
        except ValueError:
            raise SystemExit(sys.argv[0] + ': You must specific an integer for chunksize.')
        if self._max_size < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for chunksize.')


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
        except (syslib.SyslibError, SystemExit) as exception:
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

    def _copy(self, ifile, ofile):
        chunks, lchunk = divmod(self._max_size, self._cache_size)
        for i in [self._cache_size]*chunks + [lchunk]:
            chunk = ifile.read(i)
            if not chunk:
                break
            ofile.write(chunk)

    def run(self):
        """
        Start program
        """
        options = Options()
        self._cache_size = 131072
        self._max_size = options.get_max_size()

        try:
            with open(options.get_file(), 'rb') as ifile:
                for part in range(int(syslib.FileStat(
                        options.get_file()).get_size()/options.get_max_size() + 1)):
                    try:
                        file = options.get_file() + '.' + str(part + 1).zfill(3)
                        with open(file, 'wb') as ofile:
                            print(file + '...')
                            self._copy(ifile, ofile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                         str(part + 1).zfill(3) + '" file.')
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + options.get_file() + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
