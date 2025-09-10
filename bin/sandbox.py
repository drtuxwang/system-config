#!/usr/bin/env python3
"""
Sandbox command/shell with disk and network restrictions.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from network_mod import Sandbox, SandboxFile
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_command(self) -> Sandbox:
        """
        Return command Command class object.
        """
        return self._command

    def _parse_args(self, args: List[str]) -> List[str]:
        parser = argparse.ArgumentParser(
            description="Sandbox command/shell with "
            "disk, sound and network restrictions.",
        )

        parser.add_argument(
            '-net',
            dest='allow_net',
            action='store_true',
            help="Allow external network access.",
        )

        parser.add_argument(
            '-mounts',
            dest='allow_mounts',
            action='store_true',
            help="Mount full disk access.",
        )

        parser.add_argument(
            'command',
            nargs='?',
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
    def _get_command(command: str, args: List[str]) -> Sandbox:
        if Path(command).is_file():
            return SandboxFile(Path(command).resolve())

        return Sandbox(command, args=args, errors='stop')

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        command_args = self._parse_args(args[1:])

        self._command = (
            self._get_command(self._args.command, command_args)
            if self._args.command
            else self._get_command('bash', ['-l'])
        )

        if self._args.allow_mounts:
            configs = ['/']
        else:
            home = str(Path.home())
            configs = [
                f'{Path(home, x)}:ro'
                for x in (
                    '.bashrc',
                    '.cache/ibus',
                    '.config/ibus',
                    '.profile',
                    '.tmux.conf',
                    '.vimrc',
                )
                if Path(home, x).exists()
            ]

            work_dir = os.environ['PWD']
            if work_dir == home:
                desktop = Path(work_dir, 'Desktop')
                if desktop.is_dir():
                    os.chdir(desktop)
                    work_dir = str(desktop)
            configs.append(work_dir)

        if self._args.allow_net:
            configs.append('net')
        self._command.sandbox(configs, errors='stop')


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

        print("\x1b[1;34mSandbox: Starting...\x1b[0m")
        exitcode = Task(options.get_command().get_cmdline()).run()
        print("\x1b[1;34mSandbox: Shutdown!\x1b[0m")
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
