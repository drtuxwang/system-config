#!/usr/bin/env python3
"""
Unpack a compressed archive in RAR format.
"""

import argparse
import os
import signal
import sys
from typing import List

from command_mod import Command
from subtask_mod import Exec, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archiver(self) -> Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self) -> List[str]:
        """
        Return list of archives files.
        """
        return self._args.archives

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in RAR format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            '-test',
            dest='test_flag',
            action='store_true',
            help="Test archive data only.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.rar',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._archiver = Command('unrar', errors='stop')
        if args[1] in ('l', 't', 'x'):
            self._archiver.set_args(args[1:])
            Exec(self._archiver.get_cmdline()).run()

        if self._args.view_flag:
            self._archiver.set_args(['l', '-std'])
        elif self._args.test_flag:
            self._archiver.set_args(['t', '-std'])
        else:
            self._archiver.set_args(['x', '-std'])


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

        os.umask(0o022)

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        archiver = options.get_archiver()

        for archive in options.get_archives():
            task = Task(archiver.get_cmdline() + [archive])
            task.run()
            if task.get_exitcode():
                print(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                    file=sys.stderr
                )
                raise SystemExit(task.get_exitcode())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
