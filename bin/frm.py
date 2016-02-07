#!/usr/bin/env python3
"""
Remove files or directories.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

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

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Remove files or directories.')

        parser.add_argument('-R', dest='recursiveFlag', action='store_true',
                            help='Remove directories recursively.')

        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

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
    def _rmfile(file):
        print('Removing "' + file + '" file...')
        try:
            os.remove(file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot remove "' + file + '" file.')

    def _rmdir(self, directory):
        if self._options.get_recursive_flag():
            print('Removing "' + directory + '" directory recursively...')
            try:
                shutil.rmtree(directory)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot remove "' + directory + '" directory.')
        else:
            print(sys.argv[0] + ': Ignoring "' + directory + '" directory.')

    def run(self):
        """
        Start program
        """
        self._options = Options()

        for file in self._options.get_files():
            if os.path.isfile(file):
                self._rmfile(file)
            elif os.path.isdir(file):
                self._rmdir(file)
            else:
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file or directory.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
