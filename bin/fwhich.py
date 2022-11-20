#!/usr/bin/env python3
"""
Locate a program file.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_all_flag(self) -> bool:
        """
        Return all flag.
        """
        return self._args.all_flag

    def get_extensions(self) -> List[str]:
        """
        Return list of executable extensions.
        """
        return self._extensions

    def get_programs(self) -> List[str]:
        """
        Return list of programs.
        """
        return self._args.programs

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Locate a program file.",
        )

        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help="Show the location of all occurances.",
        )
        parser.add_argument(
            'programs',
            nargs='+',
            metavar='program',
            help="Command to search.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._extensions = (
                os.environ['PATHEXT'].lower().split(os.pathsep) +
                ['.py', '']
            )
        else:
            self._extensions = ['']


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

    def _locate(self, program: str) -> None:
        found = []
        for directory in self._path.split(os.pathsep):
            if os.path.isdir(directory):
                for extension in self._options.get_extensions():
                    file = os.path.join(directory, program) + extension
                    if file not in found and os.path.isfile(file):
                        found.append(file)
                        print(file)
                        if not self._options.get_all_flag():
                            return

        if not found:
            print(program, 'not in:')
            for directory in self._path.split(os.pathsep):
                print(" ", directory)
        raise SystemExit(1)

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        self._path = os.environ['PATH']
        for program in self._options.get_programs():
            self._locate(program)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
