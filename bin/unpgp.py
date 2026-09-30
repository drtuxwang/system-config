#!/usr/bin/env python3
"""
Unpack an encrypted archive in PGP format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Task


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

    def get_sq(self) -> Command:
        """
        Return sq Command class object.
        """
        return self._sq

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack an encrypted archive in gpg "
            "(pgp compatible) format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.gpg|file.pgp',
            help="GPG/PGP encrypted file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._sq = Command('sq', errors='stop')


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
        view_flag = options.get_view_flag()
        sq = options.get_sq()

        for path in [Path(x) for x in options.get_files()]:
            if path.is_file() and path.suffix in ('.pgp', '.gpg'):
                if view_flag:
                    task = Task(sq.get_cmdline() + ['inspect', path])
                    task.run(pattern='^$')
                else:
                    path_new = path.with_name(path.stem)
                    task = Task(sq.get_cmdline() + [
                        'decrypt',
                        '--overwrite',
                        '--output',
                        path_new,
                        path,
                    ])
                    task.run(pattern='^$')
                    if path_new.is_file():
                        file_time = int(path.stat().st_mtime)
                        os.utime(path_new, (file_time, file_time))
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
