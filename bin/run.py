#!/usr/bin/env python3
"""
Run a command immune to terminal hangups.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command, CommandFile
from subtask_mod import Daemon


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_command(self) -> Command:
        """
        Return command Command class object.
        """
        return self._command

    def get_log_file(self) -> str:
        """
        Return log file.
        """
        return self._args.log_file

    def _parse_args(self, args: List[str]) -> List[str]:
        parser = argparse.ArgumentParser(
            description="Run a command immune to terminal hangups.",
        )

        parser.add_argument(
            '-q',
            action='store_const',
            const='',
            dest='log_file',
            default='run.out',
            help="Do not create 'run.out' output file.",
        )
        parser.add_argument(
            'command',
            nargs=1,
            help="Command to run.",
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help="Command argument.",
        )

        my_args = []
        for arg in args:
            my_args.append(arg)
            if not arg.startswith('-'):
                break

        self._args = parser.parse_args(my_args)

        return args[len(my_args):]

    @staticmethod
    def _get_command(directory: str, command: str) -> Command:
        if Path(command).is_file():
            return CommandFile(Path(command).resolve())

        path = Path(directory, command)
        if path.is_file():
            return CommandFile(path)
        return Command(command)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        command_args = self._parse_args(args[1:])

        self._command = self._get_command(
            str(Path(args[0]).parent),
            self._args.command[0]
        )
        self._command.set_args(command_args)

        if self._args.log_file:
            try:
                Path(self._args.log_file).touch()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{self._args.log_file}" logfile file.',
                ) from exception


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

        Daemon(
            options.get_command().get_cmdline()
        ).run(file=options.get_log_file())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
