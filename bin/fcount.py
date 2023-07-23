#!/usr/bin/env python3
"""
Count number of lines and maximum columns used in file.
"""

import argparse
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
        return [os.path.expandvars(x) for x in self._args.files]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Count number of lines and maximum "
            "columns used in file.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to examine.",
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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            if path.is_file():
                nlines = 0
                maxcols = 0
                try:
                    with path.open(errors='replace') as ifile:
                        for line in ifile:
                            nlines += 1
                            ncols = len(line.rstrip('\n'))
                            if ncols > maxcols:
                                maxcols = ncols
                                lline = nlines
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{path}" file.',
                    ) from exception
                except UnicodeDecodeError:  # Non text file
                    continue
                print(
                    f"{path}: {nlines} lines (max length of {maxcols} "
                    f"on line {lline})",
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
