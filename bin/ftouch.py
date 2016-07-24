#!/usr/bin/env python3
"""
Modify access times of all files in directory recursively.
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

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Modify access times of all files in directory '
            'recursively.')

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory containing files to touch.'
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

    def _toucher(self, directory):
        print(directory)
        if os.path.isdir(directory):
            try:
                files = [
                    os.path.join(directory, x)
                    for x in os.listdir(directory)
                ]
                subtask_mod.Batch(self._touch.get_cmdline() + files).run()
                for file in files:
                    if os.path.isdir(file) and not os.path.islink(file):
                        self._toucher(file)
            except PermissionError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot open "' + directory +
                    '" directory.'
                )

    def run(self):
        """
        Start program
        """
        options = Options()

        self._touch = command_mod.Command('touch', args=['-a'], errors='stop')
        for directory in options.get_directories():
            self._toucher(directory)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
