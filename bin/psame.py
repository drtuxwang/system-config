#!/usr/bin/env python3
"""
Show picture files with same finger print.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


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
        return self._args.recursive_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show picture files with same finger print.')

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|directory',
            help='File or directory containing files to compare'
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

        findimagedupes = command_mod.Command('findimagedupes', errors='stop')
        if options.get_recursive_flag():
            findimagedupes.append_arg('-R')
        findimagedupes.extend_args(options.get_files())

        task = subtask_mod.Batch(findimagedupes.get_cmdline())
        task.run()
        for line in sorted(task.get_output()):
            print('***', line, '***')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
