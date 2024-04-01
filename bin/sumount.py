#!/usr/bin/env python3
"""
Unmount file system securely mounted with SSH protocol.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unmount file system securely mounted with "
            "SSH protocol.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='localpath',
            help="Local directory",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._directories = []
        for path in [Path(x) for x in args[1:]]:
            self._directories.append(str(path.resolve()))


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

        directories = options.get_directories()
        mount = Command('mount', errors='stop')
        fusermount = Command('fusermount', errors='stop')

        for directory in directories:
            task = Batch(mount.get_cmdline())
            task.run(pattern=f' {directory} type fuse.sshfs ')
            if not task.has_output():
                raise SystemExit(
                    f'{sys.argv[0]}: "{directory}" is not a mount point.',
                )
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            fusermount.set_args(['-u', directory])
            Task(fusermount.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
