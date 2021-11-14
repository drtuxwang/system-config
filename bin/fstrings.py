#!/usr/bin/env python3
"""
Print the strings of printable characters in files.
"""

import argparse
import glob
import os
import signal
import sys
from typing import BinaryIO, List


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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Print the strings of printable characters in files.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to search.",
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

    def _file(self, file: str) -> None:
        try:
            with open(file, 'rb') as ifile:
                self._pipe(ifile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

    @staticmethod
    def _pipe(pipe: BinaryIO) -> None:
        string = ''
        while True:
            data = pipe.read(4096)
            if not data:
                break
            for byte in data:
                if 31 < byte < 127:
                    string += chr(byte)
                else:
                    if len(string) >= 4:
                        print(string)
                    string = ''
        if string:
            print(string)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if not options.get_files():
            self._pipe(sys.stdin.buffer)
        else:
            for file in options.get_files():
                self._file(file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
