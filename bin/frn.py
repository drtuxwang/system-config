#!/usr/bin/env python3
"""
Rename file/directory by replacing some characters.
"""

import argparse
import glob
import os
import re
import shutil
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
            description='Rename file/directory by replacing some characters.',
        )

        parser.add_argument(
            'pattern',
            nargs=1,
            help='Regular expression.'
        )
        parser.add_argument(
            'replacement',
            nargs=1,
            help='Replacement for matches.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error as exception:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' +
                options.get_pattern() + '".'
            ) from exception

        self._replacement = options.get_replacement()
        self._files = options.get_files()

        for file in self._files:
            if os.sep in file:
                newfile = os.path.join(
                    os.path.dirname(file),
                    self._is_match.sub(
                        self._replacement,
                        os.path.basename(file)
                    )
                )
            else:
                newfile = self._is_match.sub(self._replacement, file)
            if newfile != file:
                print('Renaming "' + file + '" to "' + newfile + '"...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename over existing "' +
                        newfile + '" file.'
                    )
                try:
                    shutil.move(file, newfile)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename to "' +
                        newfile + '" file.'
                    ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
