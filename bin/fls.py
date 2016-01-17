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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_files(self):
        """
        Return list of files.
        """
        return self._files

    def get_order(self):
        """
        Return display order.
        """
        return self._args.order

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def get_reverse_flag(self):
        """
        Return reverse flag.
        """
        return self._args.reverseFlag

    def _parse_args(self, args):
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


class List(object):
    """
    List class
    """

    def __init__(self, options):
        self._list(options, options.get_files())

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
            print('{0:10d} [{1:s}] {2:s}'.format(fileStat.get_size(), fileStat.get_time_local(),
                                                 fileStat.get_file()))
            if options.get_recursive_flag() and fileStat.get_file().endswith(os.sep):
                self._list(options, sorted(glob.glob(fileStat.get_file() + '.*') +
                           glob.glob(fileStat.get_file() + '*')))
        return

    def _sorted(self, options, fileStats):
        order = options.get_order()
        if order == 'ctime':
            fileStats = sorted(fileStats, key=lambda s: s.get_time_create())
        elif order == 'mtime':
            fileStats = sorted(fileStats, key=lambda s: s.get_time())
        elif order == 'size':
            fileStats = sorted(fileStats, key=lambda s: s.get_size())
        if options.get_reverse_flag():
            return reversed(fileStats)
        else:
            return fileStats


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
            List(options)
        except KeyboardInterrupt:
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
