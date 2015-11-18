#!/usr/bin/env python3
"""
Replace symbolic link to files with copies.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import shutil
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
        parser = argparse.ArgumentParser(description='Replace symbolic link to files with copies.')

        parser.add_argument('files', nargs='+', metavar='file',
                            help='Symbolic link to file.')

        self._args = parser.parse_args(args)


class Copylink:

    def __init__(self, options):
        for file in options.getFiles():
            if os.path.islink(file):
                try:
                    link = os.readlink(file)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" link.')
                target = os.path.join(os.path.dirname(file), link)
                if os.path.isfile(target):
                    print('Copy file:', file, '->', target)
                    self._copy(file, link, target)
                elif not os.path.isdir(target):
                    print('Null link:', file, '->', link)
            elif not os.path.exists(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')

    def _copy(self, file, link, target):
        try:
            os.remove(file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot remove "' + file + '" link.')
        try:
            shutil.copy2(target, file)
        except IOError as exception:
            if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                raise SystemExit(sys.argv[0] + ': Cannot copy "' + target + '" file.')
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Copylink(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
