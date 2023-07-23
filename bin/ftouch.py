#!/usr/bin/env python3
"""
Modify access times of all files in directory recursively.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return [os.path.expandvars(x) for x in self._args.directories]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Modify access times of all files in directory "
            "recursively.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing files to touch.",
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

    def _toucher(self, directory_path: Path) -> None:
        print(directory_path)
        if directory_path.is_dir():
            try:
                paths = list(directory_path.iterdir())
                subtask_mod.Batch(
                    self._touch.get_cmdline() + [str(x) for x in paths]
                ).run()
                for path in paths:
                    if path.is_dir() and not path.is_symlink():
                        self._toucher(path)
            except PermissionError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot open '
                    f'"{directory_path}" directory.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._touch = command_mod.Command('touch', args=['-a'], errors='stop')
        for directory in options.get_directories():
            self._toucher(Path(directory))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
