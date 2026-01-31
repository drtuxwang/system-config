#!/usr/bin/env python3
"""
Make a compressed archive in ZIP format.
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
        return self._archive

    def get_archiver(self) -> Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a compressed archive in ZIP format.")

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.zip',
            help="Archive file or directory.",
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
        if os.name == 'nt':
            self._archiver = Command('pkzip32.exe', errors='ignore')
            if self._archiver.is_found():
                self._archiver.set_args(
                    ['-add', '-maximum', '-recurse', '-path'])
            else:
                self._archiver = Command(
                    'zip',
                    args=['-r', '-9'],
                    errors='stop'
                )
        else:
            self._archiver = Command('zip', args=['-r', '-9'], errors='stop')

        if len(args) > 1 and args[1] in ('-add', '-r'):
            Exec(self._archiver.get_cmdline() + args[1:]).run()

        self._parse_args(args[1:])

        path = Path(self._args.archive[0])
        self._archive = f'{path.resolve()}.zip' if path.is_dir() else str(path)
        if '.zip' not in self._archive:
            raise SystemExit(
                f'{sys.argv[0]}: Unsupported "{self._archive}" archive format.'
            )

        self._archiver.append_arg(self._archive)
        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())


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

        os.umask(0o022)

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        archive = options.get_archive()

        task = Exec(options.get_archiver().get_cmdline())
        task.run()
        if task.get_exitcode():
            raise OSError
        try:
            if Path(archive).exists():
                Path(archive).replace(f'{archive}.orig')
            Path(f'{archive}.part').replace(archive)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{archive}" archive file.',
            ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
