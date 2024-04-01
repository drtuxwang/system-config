#!/usr/bin/env python3
"""
Substitute patterns on lines in files.
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

from file_mod import FileStat


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

    def get_pattern(self) -> str:
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def get_replacement(self) -> str:
        """
        Return replacement.
        """
        return self._args.replacement[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Substitute patterns on lines in files.",
        )

        parser.add_argument(
            'pattern',
            nargs=1,
            help="Regular expression.",
        )
        parser.add_argument(
            'replacement',
            nargs=1,
            help="Replacement for matches.",
        )
        parser.add_argument(
            'files',
            nargs='+',
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _remove(*paths: Path) -> None:
        for path in paths:
            try:
                path.unlink()
            except OSError:
                pass

    def _replace(self, path: Path) -> None:
        path_new = Path(f'{path}.part')
        nchange = 0

        try:
            with path.open(errors='replace') as ifile:
                try:
                    with path_new.open('w') as ofile:
                        for line in ifile:
                            line_new = self._is_match.sub(
                                self._replacement, line)
                            print(line_new, end='', file=ofile)
                            if line_new != line:
                                nchange += 1
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{path_new}" file.'
                    ) from exception
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.',
            ) from exception

        if nchange:
            if nchange > 1:
                print(f"{path}: {nchange} lines changed.")
            else:
                print(f"{path}: {nchange} line changed.")

            try:
                os.chmod(path_new, FileStat(path).get_mode())
                path_new.replace(path)
            except OSError as exception:
                self._remove(path_new)
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update "{path}" file.',
                ) from exception
        else:
            self._remove(path_new)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Invalid regular expression '
                f'"{options.get_pattern()}".',
            ) from exception

        self._replacement = options.get_replacement()
        self._files = options.get_files()

        for path in [Path(x) for x in self._files]:
            if path.is_file():
                self._replace(path)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
