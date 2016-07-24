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
        parser = argparse.ArgumentParser(
            description='Replace symbolic link to files with copies.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Symbolic link to file.'
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
    def _copy(file, target):
        try:
            os.remove(file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot remove "' + file + '" link.')

        try:
            shutil.copy2(target, file)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy "' + target + '" file.')

    def run(self):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.islink(file):
                try:
                    link = os.readlink(file)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" link.')
                target = os.path.join(os.path.dirname(file), link)
                if os.path.isfile(target):
                    print('Copy file:', file, '->', target)
                    self._copy(file, target)
                elif not os.path.isdir(target):
                    print('Null link:', file, '->', link)
            elif not os.path.exists(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
