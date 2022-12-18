#!/usr/bin/env python3
"""
Show file disk usage.
"""

import argparse
import glob
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_summary_flag(self) -> bool:
        """
        Return summary flag.
        """
        return self._args.summary_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Show file disk usage.")

        parser.add_argument(
            '-s',
            dest='summary_flag',
            action='store_true',
            help="Show summary only.",
        )
        parser.add_argument(
            'files',
            nargs='*',
            default=[os.curdir],
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _usage(self, options: Options, directory_path: Path) -> int:
        size = 0
        try:
            paths = sorted(directory_path.iterdir())
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{directory_path}" directory.',
            ) from exception
        for path in paths:
            if not path.is_symlink():
                if path.is_dir():
                    size += self._usage(options, path)
                else:
                    size += int((path.stat().st_size + 1023) / 1024)
        if not options.get_summary_flag():
            print(f"{size:7d} {directory_path}")
        return size

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            if path.is_symlink():
                print(f"{0:7d} {path}")
            else:
                if path.is_dir():
                    size = self._usage(options, path)
                    if options.get_summary_flag():
                        print(f"{size:7d} {path}")
                elif path.is_file():
                    size = int((path.stat().st_size + 1023) / 1024)
                    print(f"{size:7d} {path}")
                else:
                    print(f"{0:7d} {path}")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
