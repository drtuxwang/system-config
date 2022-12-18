#!/usr/bin/env python3
"""
Securely backup/restore partitions using SSH protocol.
"""

import argparse
import glob
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

    def get_command_1(self) -> command_mod.Command:
        """
        Return command1 Command class object.
        """
        return self._command1

    def get_command_2(self) -> command_mod.Command:
        """
        Return command2 Command class object.
        """
        return self._command2

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Securely backup/restore partitions using "
            "SSH protocol.",
        )

        parser.add_argument(
            'source',
            nargs=1,
            metavar='[[user1@]host1:]source',
            help="Source device/file location.",
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='[[user1@]host1:]target',
            help="Target device/file location.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        source = self._args.source[0]
        target = self._args.target[0]
        if ':' in source:
            if ':' in target:
                raise SystemExit(
                    f"{sys.argv[0]}: Source or target cannot both be "
                    "remote device/file.",
                )
            host, file = source.split(':')[:2]
            device = target
            print(f'Restoring "{device}" from {host}:{file}...')
            self._command1 = command_mod.Command(
                'ssh',
                args=[host, f'cat {file}'],
                errors='stop'
            )
            self._command2 = command_mod.Command(
                'dd',
                args=[f'of={device}'],
                errors='stop'
            )
        else:
            if ':' not in target:
                raise SystemExit(
                    f'{sys.argv[0]}: Source or target cannot both be '
                    'local device/file.',
                )
            if not Path(source).exists():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{source}" device or file.',
                )
            device = source
            host, file = target.split(':')[:2]
            print(f'Backing up "{device}" to {host}:{file}...')
            self._command1 = command_mod.Command(
                'dd',
                args=[f'if={device}'],
                errors='stop'
            )
            self._command2 = command_mod.Command(
                'ssh',
                args=[f'{host} cat - > {file}'],
                errors='stop'
            )


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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        task = subtask_mod.Task(options.get_command_1().get_cmdline() + ['|'] +
                                options.get_command_2().get_cmdline())
        task.run()
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
