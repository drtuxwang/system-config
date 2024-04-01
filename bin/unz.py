#!/usr/bin/env python3
"""
Unpack a compressed archive using suitable tool.",
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

    def get_archives(self) -> List[str]:
        """
        Return list of archive files.
        """
        return self._args.archives

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive using suitable tool.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='archive',
            help="Archive file.",
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

        os.umask(0o022)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        view_args = ['-v'] if options.get_view_flag() else []

        for path in [Path(x) for x in options.get_archives()]:
            args = view_args + [path]
            suffix = path.suffix
            if path.name.endswith((
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
                command = Command('untar', errors='stop')
            elif suffix in (
                '.ace',
                '.deb',
                '.gpg',
                '.pdf',
                '.squashfs',
                '.zst',
                '.zstd',
            ):
                command = Command(f'un{suffix[1:]}', errors='stop')
            elif suffix in ('.pyc', 'unsqlite'):
                command = Command(f'un{suffix[1:]}', errors='stop')
                args = [path]
            elif suffix == 'initr':
                command = Command('uninitrd', errors='stop')
            else:
                command = Command('un7z', errors='stop')
            cmdline = command.get_cmdline() + args
            print(f"\nRunning: {command.args2cmd(cmdline)}")
            task = Task(cmdline)
            task.run()
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
