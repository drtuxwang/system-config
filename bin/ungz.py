#!/usr/bin/env python3
"""
Uncompress a file in GZIP format.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_gzip(self):
        """
        Return gzip Command class object.
        """
        return self._gzip

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Uncompress a file in GZIP format.')

        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.gz',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gzip = command_mod.Command('gzip', errors='stop')
        self._gzip.set_args(['-d'] + self._args.archives)


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

        subtask_mod.Exec(options.get_gzip().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
