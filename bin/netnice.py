#!/usr/bin/env python3
"""
Run a command with limited network bandwidth.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import network_mod
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

    def get_netnice(self) -> command_mod.Command:
        """
        Return NetNice Command class object.
        """
        return self._netnice

    def _parse_args(self, args: List[str]) -> command_mod.Command:
        parser = argparse.ArgumentParser(
            description='Run a command with limited network bandwidth.',
        )

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='drate',
            default=[0],
            help='Download rate limit in kps. Default is set in '
            '".config/netnice.json".'
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
        while args:
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            if args[0] == '-n' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

        if self._args.drate[0] < 0:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'download rate limit.'
            )

        if os.path.isfile(self._args.command[0]):
            return command_mod.CommandFile(
                self._args.command[0],
                args=args[len(my_args):]
            )
        return command_mod.Command(
            self._args.command[0], args=args[len(my_args):], errors='stop')

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._command = self._parse_args(args[1:])
        self._netnice = network_mod.NetNice(self._args.drate[0], errors='stop')


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

        cmdline = options.get_command().get_cmdline()
        netnice = options.get_netnice()
        if netnice.is_found():
            cmdline = netnice.get_cmdline() + cmdline
        task = subtask_mod.Task(cmdline)
        task.run()

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
