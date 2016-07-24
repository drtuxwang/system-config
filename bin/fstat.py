#!/usr/bin/env python3
"""
Display file status.
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
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Display file status.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
        )

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
            file_stat = file_mod.FileStat(file)
            print('"' + file + '".mode  =', oct(file_stat.get_mode()))
            print('"' + file + '".ino   =', file_stat.get_inode_number())
            print('"' + file + '".dev   =', file_stat.get_inode_device())
            print('"' + file + '".nlink =', file_stat.get_number_links())
            print('"' + file + '".uid   =', file_stat.get_userid())
            print('"' + file + '".gid   =', file_stat.get_groupid())
            print('"' + file + '".size  =', file_stat.get_size())
            print('"' + file + '".atime =', file_stat.get_time_access())
            print('"' + file + '".mtime =', file_stat.get_time())
            print('"' + file + '".ctime =', file_stat.get_time_change())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
