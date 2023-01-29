#!/usr/bin/env python3
"""
Locate a program file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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
                os.environ['PATHEXT'].lower().split(os.pathsep) + ['.py', '']
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    def _locate(self, program: str) -> None:
        found = []
        for path in [Path(x) for x in self._path.split(os.pathsep)]:
            if path.is_dir():
                for extension in self._options.get_extensions():
                    path = Path(f'{Path(path, program)}{extension}')
                    if path not in found and path.is_file():
                        found.append(path)
                        print(path)
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
