#!/usr/bin/env python3
"""
Show full list of files.
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
        return self._files

    def getOrder(self):
        """
        Return display order.
        """
        return self._args.order

    def getRecursiveFlag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def getReverseFlag(self):
        """
        Return reverse flag.
        """
        return self._args.reverseFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Show full list of files.')

        parser.add_argument('-R', dest='recursiveFlag', action='store_true',
                            help='Show directories recursively.')
        parser.add_argument('-s', action='store_const', const='size', dest='order',
                            default='name', help='Sort by size of file.')
        parser.add_argument('-t', action='store_const', const='mtime', dest='order',
                            default='name', help='Sort by modification time of file.')
        parser.add_argument('-c', action='store_const', const='ctime', dest='order',
                            default='name', help='Sort by creation time of file.')
        parser.add_argument('-r', dest='reverseFlag', action='store_true',
                            help='Reverse order.')

        parser.add_argument('files', nargs='*', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = sorted(os.listdir())


class List:

    def __init__(self, options):
        self._list(options, options.getFiles())

    def _list(self, options, files):
        fileStats = []
        for file in files:
            if os.path.islink(file):
                fileStats.append(syslib.FileStat(file, size=0))
            elif os.path.isdir(file):
                fileStats.append(syslib.FileStat(file + os.sep))
            elif os.path.isfile(file):
                fileStats.append(syslib.FileStat(file))
        for fileStat in self._sorted(options, fileStats):
            print('{0:10d} [{1:s}] {2:s}'.format(fileStat.getSize(), fileStat.getTimeLocal(),
                                                 fileStat.getFile()))
            if options.getRecursiveFlag() and fileStat.getFile().endswith(os.sep):
                self._list(options, sorted(glob.glob(fileStat.getFile() + '.*') +
                           glob.glob(fileStat.getFile() + '*')))
        return

    def _sorted(self, options, fileStats):
        order = options.getOrder()
        if order == 'ctime':
            fileStats = sorted(fileStats, key=lambda s: s.getTimeCreate())
        elif order == 'mtime':
            fileStats = sorted(fileStats, key=lambda s: s.getTime())
        elif order == 'size':
            fileStats = sorted(fileStats, key=lambda s: s.getSize())
        if options.getReverseFlag():
            return reversed(fileStats)
        else:
            return fileStats


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            List(options)
        except KeyboardInterrupt:
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
