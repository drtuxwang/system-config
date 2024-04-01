#!/usr/bin/env python3
"""
Make a compressed archive using suitable tool.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archive(self) -> str:
        """
        Return archive location.
        """
        return self._args.archive[0]

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a compressed archive using suitable tool.",
        )

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='archive',
            help="Archive file.",
        )
        parser.add_argument(
            'files',
            nargs='*',
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

    @classmethod
    def run(cls) -> None:
        """
        Start program
        """
        options = Options()
        path = Path(options.get_archive())

        name = path.name.replace('-new', '')
        if name.endswith((
            '.tar',
            '.tar.gz',
            '.tar.bz2',
            '.tar.zst',
            '.tar.zstd',
            '.tar.lzma',
            '.tar.xz',
            '.tar.7z',
            '.tgz',
            '.tbz',
            '.tzs',
            '.tzst',
            '.tlz',
            '.txz',
            '.t7z',
        )):
            command = Command('tar.py', errors='stop')
        elif name.endswith('.zip'):
            command = Command('zip', errors='stop')
        elif name.endswith(('.7z', '.exe')) or path.is_dir():
            command = Command('7z', errors='stop')
        else:
            raise SystemExit(
                f"{sys.argv[0]}: Unable to make unsupported archive format:"
                f"{name}"
            )

        command.set_args([path] + options.get_files())
        Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
