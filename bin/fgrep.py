#!/usr/bin/env python3
"""
Print lines matching a pattern.
"""

import argparse
import glob
import os
import re
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

    def get_ignore_case_flag(self) -> bool:
        """
        Return ignore case flag.
        """
        return self._args.ignoreCase_flag

    def get_invert_flag(self) -> bool:
        """
        Return invert regular expression flag.
        """
        return self._args.invert_flag

    def get_number_flag(self) -> bool:
        """
        Return line number flag.
        """
        return self._args.number_flag

    def get_pattern(self) -> str:
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Print lines matching a pattern.",
        )

        parser.add_argument(
            '-i',
            dest='ignoreCase_flag',
            action='store_true',
            help="Ignore case distinctions.",
        )
        parser.add_argument(
            '-n',
            dest='number_flag',
            action='store_true',
            help="Prefix each line of output with line number.",
        )
        parser.add_argument(
            '-v',
            dest='invert_flag',
            action='store_true',
            help="Invert the sense of matching.",
        )
        parser.add_argument(
            'pattern',
            nargs=1,
            help="Regular expression.",
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

    def _file(self, options: Options, file: str, prefix: str = '') -> None:
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                self._pipe(options, ifile, prefix)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

    def _pipe(self, options: Options, pipe: TextIO, prefix: str = '') -> None:
        number = 0
        if options.get_invert_flag():
            for line in pipe:
                line = line.rstrip('\r\n')
                number += 1
                if not self._is_match.search(line):
                    if options.get_number_flag():
                        line = f'{number}:{line}'
                    try:
                        print(f"{prefix}{line}")
                    except OSError as exception:
                        raise SystemExit(0) from exception
        else:
            for line in pipe:
                line = line.rstrip('\r\n')
                number += 1
                if self._is_match.search(line):
                    if options.get_number_flag():
                        line = f'{number}:{line}'
                    try:
                        print(f"{prefix}{line}")
                    except OSError as exception:
                        raise SystemExit(0) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        try:
            if options.get_ignore_case_flag():
                self._is_match = re.compile(
                    options.get_pattern(), re.IGNORECASE)
            else:
                self._is_match = re.compile(options.get_pattern())
        except re.error as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Invalid regular expression '
                f'"{options.get_pattern()}".',
            ) from exception
        if len(options.get_files()) > 1:
            for file in options.get_files():
                self._file(options, file, prefix=file + ':')
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
