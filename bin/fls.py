#!/usr/bin/env python3
"""
Show full list of files.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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
        return self._args.recursive_flag

    def get_reverse_flag(self):
        """
        Return reverse flag.
        """
        return self._args.reverse_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Show full list of files.')

        parser.add_argument('-R', dest='recursive_flag', action='store_true',
                            help='Show directories recursively.')
        parser.add_argument('-s', action='store_const', const='size', dest='order',
                            default='name', help='Sort by size of file.')
        parser.add_argument('-t', action='store_const', const='mtime', dest='order',
                            default='name', help='Sort by modification time of file.')
        parser.add_argument('-c', action='store_const', const='ctime', dest='order',
                            default='name', help='Sort by meta data change time of file.')
        parser.add_argument('-r', dest='reverse_flag', action='store_true',
                            help='Reverse order.')

        parser.add_argument('files', nargs='*', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = sorted(os.listdir())


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

    def _list(self, options, files):
        file_stats = []
        for file in files:
            if os.path.islink(file):
                file_stats.append(file_mod.FileStat(file, size=0))
            elif os.path.isdir(file):
                file_stats.append(file_mod.FileStat(file + os.sep))
            elif os.path.isfile(file):
                file_stats.append(file_mod.FileStat(file))
        for file_stat in self._sorted(options, file_stats):
            print('{0:10d} [{1:s}] {2:s}'.format(file_stat.get_size(), file_stat.get_time_local(),
                                                 file_stat.get_file()))
            if options.get_recursive_flag() and file_stat.get_file().endswith(os.sep):
                self._list(options, sorted(glob.glob(
                    file_stat.get_file() + '.*') + glob.glob(file_stat.get_file() + '*')))
        return

    @staticmethod
    def _sorted(options, file_stats):
        order = options.get_order()
        if order == 'ctime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time_change())
        elif order == 'mtime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time())
        elif order == 'size':
            file_stats = sorted(file_stats, key=lambda s: s.get_size())
        if options.get_reverse_flag():
            return reversed(file_stats)
        else:
            return file_stats

    def run(self):
        """
        Start program
        """
        options = Options()

        self._list(options, options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
