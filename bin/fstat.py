#!/usr/bin/env python3
"""
Display file status.
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
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Display file status.')

        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Status(object):
    """
    Status class
    """

    def __init__(self, options):
        for file in options.get_files():
            fileStat = syslib.FileStat(file)
            name = file.replace('\\', '\\\\').replace("'", "\\'")
            print('"' + file + '".mode  =', oct(fileStat.get_mode()))
            print('"' + file + '".ino   =', fileStat.get_inode_number())
            print('"' + file + '".dev   =', fileStat.get_inode_device())
            print('"' + file + '".nlink =', fileStat.get_number_links())
            print('"' + file + '".uid   =', fileStat.get_userid())
            print('"' + file + '".gid   =', fileStat.get_groupid())
            print('"' + file + '".size  =', fileStat.get_size())
            print('"' + file + '".atime =', fileStat.get_time_access())
            print('"' + file + '".mtime =', fileStat.get_time())
            print('"' + file + '".ctime =', fileStat.get_time_create())


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
            Status(options)
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
