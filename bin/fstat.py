#!/usr/bin/env python3
"""
Display file status.
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


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Display file status.')

        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Status:

    def __init__(self, options):
        for file in options.getFiles():
            fileStat = syslib.FileStat(file)
            name = file.replace('\\', '\\\\').replace("'", "\\'")
            print('"' + file + '".mode  =', oct(fileStat.getMode()))
            print('"' + file + '".ino   =', fileStat.getInodeNumber())
            print('"' + file + '".dev   =', fileStat.getInodeDevice())
            print('"' + file + '".nlink =', fileStat.getNumberlinks())
            print('"' + file + '".uid   =', fileStat.getUserid())
            print('"' + file + '".gid   =', fileStat.getGroupid())
            print('"' + file + '".size  =', fileStat.getSize())
            print('"' + file + '".atime =', fileStat.getTimeAccess())
            print('"' + file + '".mtime =', fileStat.getTime())
            print('"' + file + '".ctime =', fileStat.getTimeCreate())


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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
