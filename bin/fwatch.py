#!/usr/bin/env python3
"""
Watch file system events.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_inotifywait(self):
        """
        Return inotifywait Command class object.
        """
        return self._inotifywait

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Watch file system events.')

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory to monitor.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._inotifywait = command_mod.Command('inotifywait', errors='stop')
        self._inotifywait.set_args([
            '-e',
            'create,modify,move,delete',
            '-mr'
        ] + self._args.directories)


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
        options = Options()

        subtask_mod.Exec(options.get_inotifywait().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
