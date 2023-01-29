#!/usr/bin/env python3
"""
Unpack a compressed archive in ZIP format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archiver(self) -> command_mod.Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self) -> List[str]:
        """
        Return list of archive files.
        """
        return self._args.archives

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in ZIP format.",
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
            metavar='file.zip',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._archiver = command_mod.Command(
                'pkzip32.exe',
                errors='ignore'
            )
            if not self._archiver.is_found():
                self._archiver = command_mod.Command('unzip', errors='stop')
        else:
            self._archiver = command_mod.Command('unzip', errors='stop')

        if args[1] in ('view', 'test'):
            self._archiver.set_args(args[1:])
            subtask_mod.Exec(self._archiver.get_cmdline()).run()

        if Path(self._archiver.get_file()).name == 'pkzip32.exe':
            if self._args.view_flag:
                self._archiver.set_args(['-view'])
            elif self._args.test_flag:
                self._archiver.set_args(['-test'])
            else:
                self._archiver.set_args(['-extract', '-directories'])
        else:
            if self._args.view_flag:
                self._archiver.set_args(['-v'])
            elif self._args.test_flag:
                self._archiver.set_args(['-t'])


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

        cmdline = options.get_archiver().get_cmdline()
        for archive in options.get_archives():
            task = subtask_mod.Task(cmdline + [archive])
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
