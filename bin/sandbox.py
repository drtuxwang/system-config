#!/usr/bin/env python3
"""
Sandbox command/shell with read/write and network restrictions.
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
            description='Sandbox command/shell with '
            'read/write and network restrictions.',
        )

        parser.add_argument(
            '-net',
            dest='allow_net',
            action='store_true',
            help='Allow external network access.'
        )

        parser.add_argument(
            '-mounts',
            dest='allow_mounts',
            action='store_true',
            help='Mount full disk access.'
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

        if self._args.allow_mounts:
            configs = ['/']
        else:
            home = os.getenv('HOME', '/')
            configs = [
                os.path.join(home, x) + ':ro'
                for x in ('.bashrc', '.profile', '.tmux.conf', '.vimrc')
                if os.path.exists(os.path.join(home, x))
            ]

            work_dir = os.environ['PWD']
            if work_dir == os.environ['HOME']:
                desktop = os.path.join(work_dir, 'Desktop')
                if os.path.isdir(desktop):
                    os.chdir(desktop)
                    work_dir = desktop
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

        print("\033[1;34mSandbox: Starting...\033[0m")
        exitcode = subtask_mod.Task(options.get_command().get_cmdline()).run()
        print("\033[1;34mSandbox: Shutdown!\033[0m")
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
