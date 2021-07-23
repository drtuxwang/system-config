#!/usr/bin/env python3
"""
Run a command without network access.
"""

import argparse
import getpass
import glob
import os
import signal
import sys
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

    def get_command(self) -> command_mod.Command:
        """
        Return command Command class object.
        """
        return self._command

    def _parse_args(self, args: List[str]) -> List[str]:
        parser = argparse.ArgumentParser(
            description='Run a command without network access.',
        )

        parser.add_argument(
            'command',
            nargs=1,
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
    def _get_command(directory: str, command: str) -> command_mod.Command:
        if os.path.isfile(command):
            return command_mod.CommandFile(os.path.abspath(command))

        file = os.path.join(directory, command)
        if os.path.isfile(file):
            return command_mod.CommandFile(file)
        return command_mod.Command(command, errors='stop')

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        command_args = self._parse_args(args[1:])

        self._command = self._get_command(
            os.path.dirname(args[0]),
            self._args.command[0]
        )
        self._command.set_args(command_args)


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
    def run() -> None:
        """
        Start program
        """
        options = Options()

        bwrap = command_mod.Command('bwrap', errors='ignore')
        if bwrap.is_found():
            print('Unsharing network namespace...')
            cmdline = bwrap.get_cmdline() + [
                '--bind',
                '/',
                '/',
                '--dev',
                '/dev',
                '--unshare-net',
                '--',
            ] + options.get_command().get_cmdline()
        else:
            cmdline = options.get_command().get_cmdline()

        subtask_mod.Exec(cmdline).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
