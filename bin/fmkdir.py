#!/usr/bin/env python3
"""
Create a single lower case directory.
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
        self._directory = None
        self.parse(sys.argv)

    def get_directory(self):
        """
        Return directory.
        """
        return self._directory

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create a single lower case directory'
        )
        parser.add_argument(
            'words',
            nargs='+',
            metavar='word',
            help='Part of directory name.'
        )

        words = parser.parse_args(args).words

        self._directory = '-'.join(words).lower()

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

    @staticmethod
    def run():
        """
        Start program
        """
        directory = Options().get_directory()

        if not os.path.isdir(directory):
            print('Creating "{0:s}"...'.format(directory))
            try:
                os.makedirs(directory)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create directory.'
                ) from exception


if '--pydoc' in sys.argv:
    help(__name__)
else:
    Main()
