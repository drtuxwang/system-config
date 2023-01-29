#!/usr/bin/env python3
"""
Output the last n lines of a file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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
        return self._lines

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Output the last n lines of a file.",
        )

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='lines',
            default=[10],
            metavar='K',
            help='Output last K lines. Use "-n +K" '
            'to output starting with Kth.',
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File to search.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if ' -n +' in f' {" ".join(args)}':
            self._lines = -self._args.lines[0]
        else:
            self._lines = self._args.lines[0]


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

    def _file(self, options: Options, file: str) -> None:
        try:
            with Path(file).open(errors='replace') as ifile:
                self._pipe(options, ifile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

    @staticmethod
    def _pipe(options: Options, pipe: TextIO) -> None:
        if options.get_lines() > 0:
            buffer: List[str] = []
            for line in pipe:
                line = line.rstrip('\n')
                buffer = (buffer + [line])[-options.get_lines():]
            for line in buffer:
                try:
                    print(line)
                except OSError as exception:
                    raise SystemExit(0) from exception
        else:
            for _ in range(-options.get_lines() - 1):
                line = pipe.readline()
                if not line:
                    break
            for line in pipe:
                try:
                    print(line.rstrip('\n'))
                except OSError as exception:
                    raise SystemExit(0) from exception

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
