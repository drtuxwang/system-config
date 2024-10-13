#!/usr/bin/env python3
"""
Compile Python source file to PYC file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_version(self) -> str:
        """
        Return python version.
        """
        return self._args.version[0]

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Compile Python source file to PYC file.",
        )

        parser.add_argument(
            '-v',
            nargs=1,
            dest='version',
            default=[None],
            help="Use different Python version (2.7, 3.11, 3.12, 3.13).",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.pyc',
            help="Python PY source file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

        os.umask(0o022)

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        version = options.get_version()

        if version:
            command = Command(f'python{version}', errors='stop')
            executable = command.get_file()
        else:
            executable = sys.executable

        for file in options.get_files():
            print(f"{Path(executable).name} -m compileall {file}")
            Task([executable, '-m', 'compileall', file]).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
