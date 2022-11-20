#!/usr/bin/env python3
"""
Substitute patterns on lines in files.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys
from typing import Any, List

import file_mod


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
    def _remove(*files: Any) -> None:
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

    def _replace(self, file: str) -> None:
        newfile = file + '.part'
        nchange = 0

        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                try:
                    with open(
                        newfile,
                        'w',
                        encoding='utf-8',
                        newline='\n',
                    ) as ofile:
                        for line in ifile:
                            line_new = self._is_match.sub(
                                self._replacement, line)
                            print(line_new, end='', file=ofile)
                            if line_new != line:
                                nchange += 1
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{newfile}" file.'
                    ) from exception
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

        if nchange:
            if nchange > 1:
                print(f"{file}: {nchange} lines changed.")
            else:
                print(f"{file}: {nchange} line changed.")

            try:
                os.chmod(newfile, file_mod.FileStat(file).get_mode())
                shutil.move(newfile, file)
            except OSError as exception:
                self._remove(newfile)
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update "{file}" file.',
                ) from exception
        else:
            self._remove(newfile)

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

        for file in self._files:
            if os.path.isfile(file):
                self._replace(file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
