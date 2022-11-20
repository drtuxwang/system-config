#!/usr/bin/env python3
"""
Watch file system events.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_inotifywait(self) -> command_mod.Command:
        """
        Return inotifywait Command class object.
        """
        return self._inotifywait

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Watch file system events.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory to monitor.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._inotifywait = command_mod.Command('inotifywait', errors='stop')
        self._inotifywait.set_args([
            '-e',
            'attrib,create,modify,move,delete',
            '-mr'
        ] + self._args.directories)


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        subtask_mod.Exec(options.get_inotifywait().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
