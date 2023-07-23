#!/usr/bin/env python3
"""
Replace symbolic link to files with copies.
"""

import argparse
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import Any, List


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
        return [os.path.expandvars(x) for x in self._args.files]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Replace symbolic link to files with copies.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Symbolic link to file.",
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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def _copy(path: Path, target_path: Path) -> None:
        try:
            path.unlink()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot remove "{path}" link.',
            ) from exception

        try:
            shutil.copy2(target_path, path)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot copy "{target_path}" file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            if path.is_symlink():
                target_path = path.resolve()
                if target_path.is_file():
                    print(f"Copy file: {path} -> {target_path}")
                    self._copy(path, target_path)
                elif not target_path.is_dir():
                    print(
                        f"Null link: {path} -> "  # type: ignore
                        f"{path.readlink()}"  # pylint: disable=no-member
                    )
            elif not path.exists():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
