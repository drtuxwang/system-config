#!/usr/bin/env python3
"""
Replace symbolic link to files with copies.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

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
        parser = argparse.ArgumentParser(description='Replace symbolic link to files with copies.')

        parser.add_argument('files', nargs='+', metavar='file',
                            help='Symbolic link to file.')

        self._args = parser.parse_args(args)


class Copylink(object):
    """
    Copy link class
    """

    def __init__(self, options):
        for file in options.get_files():
            if os.path.islink(file):
                try:
                    link = os.readlink(file)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" link.')
                target = os.path.join(os.path.dirname(file), link)
                if os.path.isfile(target):
                    print('Copy file:', file, '->', target)
                    self._copy(file, target)
                elif not os.path.isdir(target):
                    print('Null link:', file, '->', link)
            elif not os.path.exists(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')

    def _copy(self, file, target):
        try:
            os.remove(file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot remove "' + file + '" link.')

        try:
            shutil.copy2(target, file)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                raise SystemExit(sys.argv[0] + ': Cannot copy "' + target + '" file.')


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
            Copylink(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
