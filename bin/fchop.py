#!/usr/bin/env python3
"""
Chop up a file into chunks.
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

    def getFile(self):
        """
        Return file.
        """
        return self._args.file[0]

    def getMaxSize(self):
        """
        Return max size of file part.
        """
        return self._maxSize

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Chop up a file into chunks.')

        parser.add_argument('file', nargs=1, help='File to break up.')
        parser.add_argument('size', nargs=1, metavar='bytes|nMB',
                            help='Maximum chunk size to break up.')

        self._args = parser.parse_args(args)

        try:
            size = self._args.size[0]
            if size.endswith('MB'):
                self._maxSize = int(size[:-2]) * 1024**2
            else:
                self._maxSize = int(size)
        except ValueError:
            raise SystemExit(sys.argv[0] + ': You must specific an integer for chunksize.')
        if self._maxSize < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for chunksize.')


class Chop(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._cacheSize = 131072

        try:
            with open(options.getFile(), 'rb') as ifile:
                for part in range(int(syslib.FileStat(
                        options.getFile()).getSize()/options.getMaxSize() + 1)):
                    try:
                        file = options.getFile() + '.' + str(part + 1).zfill(3)
                        with open(file, 'wb') as ofile:
                            print(file + '...')
                            self._copy(ifile, ofile)
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                         str(part + 1).zfill(3) + '" file.')
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + options.getFile() + '" file.')

    def _copy(self, ifile, ofile):
        chunks, lchunk = divmod(self._options.getMaxSize(), self._cacheSize)
        for i in [self._cacheSize]*chunks + [lchunk]:
            chunk = ifile.read(i)
            if not chunk:
                break
            ofile.write(chunk)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Chop(options)
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
