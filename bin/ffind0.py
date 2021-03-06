#!/usr/bin/env python3
"""
Find zero sized files.
"""

import argparse
import glob
import os
import signal
import sys


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Find zero sized files.')

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory to search.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
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

    def _findzero(self, files):
        for file in sorted(files):
            if os.path.isdir(file):
                try:
                    self._findzero([
                        os.path.join(file, x)
                        for x in os.listdir(file)
                    ])
                except PermissionError:
                    pass
            else:
                try:
                    if os.path.getsize(file) == 0:
                        print(file)
                except OSError:
                    print(file)

    def run(self):
        """
        Start program
        """
        options = Options()

        self._findzero(options.get_directories())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
