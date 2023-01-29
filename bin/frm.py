#!/usr/bin/env python3
"""
Remove files or directories.
"""

import argparse
import os
import shutil
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Remove files or directories.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Remove directories recursively.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File or directory.",
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

    @staticmethod
    def _rmfile(path: Path) -> None:
        print(f'Removing "{path}" file...')
        try:
            path.unlink()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot remove "{path}" file.',
            ) from exception

    def _rmdir(self, path: Path) -> None:
        if self._options.get_recursive_flag():
            print(f'Removing "{path}" directory recursively...')
            try:
                shutil.rmtree(path)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove "{path}" directory.',
                ) from exception
        else:
            print(f'{sys.argv[0]}: Ignoring "{path}" directory.')

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        for path in [Path(x) for x in self._options.get_files()]:
            if path.is_file():
                self._rmfile(path)
            elif path.is_dir():
                self._rmdir(path)
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" file or directory.',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
