#!/usr/bin/env python3
"""
Run a command with restricted writes and no network
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import network_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_command(self) -> network_mod.Sandbox:
        """
        Return command Command class object.
        """
        return self._command

    def _parse_args(self, args: List[str]) -> List[str]:
        parser = argparse.ArgumentParser(
            description='Run a command with restricted writes and no network.',
        )

        parser.add_argument(
            'command',
            nargs='?',
            help='Command to run.'
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help='Command argument.'
        )

        my_args = []
        for arg in args:
            my_args.append(arg)
            if not arg.startswith('-'):
                break

        self._args = parser.parse_args(my_args)

        return args[len(my_args):]

    @staticmethod
    def _get_command(command: str, args: List[str]) -> network_mod.Sandbox:
        if os.path.isfile(os.path.abspath(command)):
            return network_mod.SandboxFile(os.path.abspath(command))

        return network_mod.Sandbox(command, args=args, errors='stop')

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        command_args = self._parse_args(args[1:])

        if self._args.command:
            self._command = self._get_command(self._args.command, command_args)
        else:
            self._command = self._get_command('bash', ['-l'])
        self._command.sandbox(nonet=True, writes=[os.getcwd()])


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
            sys.exit(exception)

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
                files = glob.glob(arg)  # Fixes Windows globbing bug
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

        print("Sandbox: Disabling external network access...")
        print("Sandbox: Disabling disk writes outside working directory...")
        exitcode = subtask_mod.Task(options.get_command().get_cmdline()).run()
        print("Sandbox: Exiting...")
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
