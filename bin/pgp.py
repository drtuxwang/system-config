#!/usr/bin/env python3
"""
Make an encrypted archive in PGP format.
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

    def get_sq(self) -> Command:
        """
        Return sq Command class object.
        """
        return self._sq

    def get_files(self) -> List[Path]:
        """
        Return list of files.
        """
        return [Path(x) for x in self._args.files]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make an encrypted archive in PGP format.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to encrypt.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._sq = Command('sq', errors='stop')
        self._sq.set_args([
           'encrypt',
           '--for-self',
           '--without-signature',
           '--binary',
           '--overwrite',
        ])
        os.umask(0o077)


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
        sq = options.get_sq()
        junk = '^Composing|^Hint|Consider signing|^$'

        for path in options.get_files():
            if path.is_file() and path.suffix not in ('.pgp', '.gpg'):
                path_new = Path(f'{path}.pgp')
                print(f"{path} => {path_new}")
                task = Task(sq.get_cmdline() + ['--output', path_new, path])
                task.run(pattern=junk)
                for line in task.get_output():
                    print(line)
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
                if path_new.is_file():
                    file_time = int(path.stat().st_mtime)
                    os.utime(path_new, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
