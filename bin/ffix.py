#!/usr/bin/env python3
"""
Remove horrible characters in filenames.
"""

import argparse
import re
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
        Return list to files.
        """
        return self._files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Remove horrible characters in filename.",
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
        if len(args) == 1 or args[1] in ('-h', '--h', '--help'):
            self._parse_args(args[1:])

        self._files = args[1:]


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

        is_bad_char = re.compile(r'^-|[ !\'$&`"()*<>?\[\]\\\\|]')
        for path in [Path(x) for x in options.get_files()]:
            path_new = Path(is_bad_char.sub('_', str(path)))
            if path_new != path and not path_new.is_file():
                if not path_new.is_dir() and not path_new.is_symlink():
                    try:
                        path.replace(path_new)
                    except OSError:
                        pass

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
