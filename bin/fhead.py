#!/usr/bin/env python3
"""
Output the first n lines of a file.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List, TextIO


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

    def get_lines(self) -> int:
        """
        Return number of lines.
        """
        return self._args.lines[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Output the first n lines of a file.")

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='lines',
            default=[10],
            metavar='K',
            help="Output first K lines.",
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File to search.",
        )

        self._args = parser.parse_args(args)

        if self._args.lines[0] < 0:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer for '
                'number of lines.',
            )

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

    def _file(self, options: Options, file: str) -> None:
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                self._pipe(options, ifile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

    @staticmethod
    def _pipe(options: Options, pipe: TextIO) -> None:
        for _ in range(options.get_lines()):
            line = pipe.readline()
            if not line:
                break
            try:
                print(line.rstrip('\r\n'))
            except OSError:
                return

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if len(options.get_files()) > 1:
            for file in options.get_files():
                print("==>", file, "<==")
                self._file(options, file)
        elif len(options.get_files()) == 1:
            self._file(options, options.get_files()[0])
        else:
            self._pipe(options, sys.stdin)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
