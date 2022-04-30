#!/usr/bin/env python3
"""
Show summary of differences between two directories recursively.
"""

import argparse
import glob
import os
import signal
import sys
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
        return self._args.directories[0]

    def get_directory_2(self) -> str:
        """
        Return directory 2.
        """
        return self._args.directories[1]

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
            sys.exit(exception)

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
    def _get_files(directory: str) -> List[str]:
        try:
            files = sorted(
                [os.path.join(directory, x) for x in os.listdir(directory)])
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
        ) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{directory}" directory.'
            ) from exception
        return files

    def _diff_dir(
        self,
        directory1: str,
        directory2: str,
        time_flag: bool = False,
    ) -> None:
        files1 = self._get_files(directory1)
        files2 = self._get_files(directory2)

        for file in files1:
            if os.path.isdir(file):
                if os.path.isdir(
                        os.path.join(directory2, os.path.basename(file)),
                ):
                    self._diff_dir(
                        file,
                        os.path.join(directory2, os.path.basename(file)),
                        time_flag,
                    )
                else:
                    print(f"only  {file}{os.sep}")
            elif os.path.isfile(file):
                if os.path.isfile(
                        os.path.join(directory2, os.path.basename(file)),
                ):
                    self._diff_file(
                        file,
                        os.path.join(directory2, os.path.basename(file)),
                        time_flag,
                    )
                else:
                    print("only ", file)

        for file in files2:
            if os.path.isdir(file):
                if not os.path.isdir(
                        os.path.join(directory1, os.path.basename(file)),
                ):
                    print(f"only  {file}{os.sep}")
            elif os.path.isfile(file):
                if not os.path.isfile(
                        os.path.join(directory1, os.path.basename(file)),
                ):
                    print("only ", file)

    @staticmethod
    def _diff_file(file1: str, file2: str, time_flag: bool = False) -> None:
        file_stat1 = file_mod.FileStat(file1)
        file_stat2 = file_mod.FileStat(file2)

        if file_stat1.get_size() != file_stat2.get_size():
            print(f"diff  {file1}  {file2}")
        elif file_stat1.get_time() != file_stat2.get_time():
            if time_flag:
                print(f"time  {file1}  {file2}")
                return
            try:
                with open(file1, 'rb') as ifile1:
                    with open(file2, 'rb') as ifile2:
                        for _ in range(0, file_stat1.get_size(), 131072):
                            if ifile1.read(131072) != ifile2.read(131072):
                                print(f"diff  {file1}  {file2}")
                                return
            except OSError:
                print(f"diff  {file1}  {file2}")
        elif file_stat1.get_size() < 65536:
            try:
                with open(file1, 'rb') as ifile1:
                    with open(file2, 'rb') as ifile2:
                        if ifile1.read(65536) != ifile2.read(65536):
                            print(f"diff  {file1}  {file2}")
            except OSError:
                print(f"diff  {file1}  {file2}")

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        directory_1 = options.get_directory_1()
        directory_2 = options.get_directory_2()
        time_flag = options.get_time_flag()

        self._diff_dir(directory_1, directory_2, time_flag)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
