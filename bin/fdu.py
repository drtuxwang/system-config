#!/usr/bin/env python3
"""
Show file disk usage.
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
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _usage(self, options: Options, directory: str) -> int:
        size = 0
        try:
            files = [os.path.join(directory, x) for x in os.listdir(directory)]
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{directory}" directory.',
            ) from exception
        for file in sorted(files):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    size += self._usage(options, file)
                else:
                    size += int((os.path.getsize(file) + 1023) / 1024)
        if not options.get_summary_flag():
            print(f"{size:7d} {directory}")
        return size

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.islink(file):
                print(f"{0:7d} {file}")
            else:
                if os.path.isdir(file):
                    size = self._usage(options, file)
                    if options.get_summary_flag():
                        print(f"{size:7d} {file}")
                elif os.path.isfile(file):
                    size = int((os.path.getsize(file) + 1023) / 1024)
                    print(f"{size:7d} {file}")
                else:
                    print(f"{0:7d} {file}")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
