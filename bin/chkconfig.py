#!/usr/bin/env python3
"""
Check BSON/JSON/YAML configuration files for errors.
"""

import argparse
import glob
import os
import signal
import sys

import config_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


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
            description='Check BSON/JSON/YAML configuration files for errors.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to check.'
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
        data = config_mod.Data()
        error = 0

        for file in options.get_files():
            if not os.path.isfile(file):
                print("{0:s}: Cannot find file".format(file))
                error = 1
            elif file.endswith(('.json', 'yaml', 'yml', '.bson')):
                try:
                    data.read(file, check=True)
                except config_mod.ReadConfigError as exception:
                    print("{0:s}: {1:s}".format(file, str(exception)))
                    error = 1

        return error


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
