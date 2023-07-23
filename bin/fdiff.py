#!/usr/bin/env python3
"""
Show summary of differences between two directories recursively.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_time_flag(self) -> bool:
        """
        Return time flag.
        """
        return self._args.time_flag

    def get_directory_1(self) -> str:
        """
        Return directory 1.
        """
        return os.path.expandvars(self._args.directories[0])

    def get_directory_2(self) -> str:
        """
        Return directory 2.
        """
        return os.path.expandvars(self._args.directories[1])

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Show summary of differences between two "
            "directories recursively.",
        )

        parser.add_argument(
            '-t',
            dest='time_flag',
            action='store_true',
            help="Compare modified time stamps.",
        )
        parser.add_argument(
            'directories',
            nargs=2,
            metavar='directory',
            help="Directory to compare.",
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
    def _get_files(path: Path) -> List[Path]:
        try:
            paths = sorted(path.iterdir())
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
        ) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{path}" directory.'
            ) from exception
        return paths

    def _diff_dir(
        self,
        path1: Path,
        path2: Path,
        time_flag: bool = False,
    ) -> None:
        for path in self._get_files(path1):
            if path.is_dir():
                if Path(path2, path.name).is_dir():
                    self._diff_dir(path, Path(path2, path.name), time_flag)
                else:
                    print(f"only  {path}/")
            elif path.is_file():
                if Path(path2, path.name).is_file():
                    self._diff_file(path, Path(path2, path.name), time_flag)
                else:
                    print(f"only  {path}")

        for path in self._get_files(path2):
            if path.is_dir():
                if not Path(path1, path.name).is_dir():
                    print(f"only  {path}/")
            elif path.is_file():
                if not Path(path1, path.name).is_file():
                    print(f"only  {path}")

    @staticmethod
    def _diff_file(path1: Path, path2: Path, time_flag: bool = False) -> None:
        file_stat1 = file_mod.FileStat(path1)
        file_stat2 = file_mod.FileStat(path2)

        if file_stat1.get_size() != file_stat2.get_size():
            print(f"diff  {path1}  {path2}")
        elif file_stat1.get_time() != file_stat2.get_time():
            if time_flag:
                print(f"time  {path1}  {path2}")
                return
            try:
                with path1.open('rb') as ifile1:
                    with path2.open('rb') as ifile2:
                        for _ in range(0, file_stat1.get_size(), 131072):
                            if ifile1.read(131072) != ifile2.read(131072):
                                print(f"diff  {path1}  {path2}")
                                return
            except OSError:
                print(f"diff  {path1}  {path2}")
        elif file_stat1.get_size() < 65536:
            try:
                with path1.open('rb') as ifile1:
                    with path2.open('rb') as ifile2:
                        if ifile1.read(65536) != ifile2.read(65536):
                            print(f"diff  {path1}  {path2}")
            except OSError:
                print(f"diff  {path1}  {path2}")

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        path1 = Path(options.get_directory_1())
        path2 = Path(options.get_directory_2())
        time_flag = options.get_time_flag()

        self._diff_dir(path1, path2, time_flag)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
