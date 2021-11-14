#!/usr/bin/env python3
"""
Open files using default application
"""

import argparse
import glob
import os
import signal
import sys
from typing import List, Tuple

import command_mod
import config_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Open files using default application.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to open.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
    def _get_program(command: List[str]) -> command_mod.Command:
        file = os.path.join(os.path.dirname(sys.argv[0]), command[0])
        if os.path.isfile(file):
            return command_mod.CommandFile(file)
        return command_mod.Command(command[0], errors='stop')

    @classmethod
    def _spawn(cls, action: Tuple[List[str], bool], file: str) -> None:
        command, daemon = action
        if not command:
            raise SystemExit(f"{sys.argv[0]}: cannot find action: {file}")
        program = cls._get_program(command)
        program.set_args(command[1:] + [file])
        cmdline = program.get_cmdline()
        print("Opening:", command_mod.Command.args2cmd(cmdline))
        if daemon:
            subtask_mod.Daemon(cmdline).run()
        else:
            subtask_mod.Task(cmdline).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        config = config_mod.Config()

        for file in options.get_files():
            if os.path.isdir(file):
                action = config.get_app('file_manager')
            elif file.split(':', 1)[0] in config.get('web_uri'):
                action = config.get_app('web_browser')
            elif not os.path.isfile(file):
                raise SystemExit(f"{sys.argv[0]}: cannot find file: {file}")
            else:
                action = config.get_open_app(
                    '.'.join(file.rsplit('.', 2)[-2:]).lower()
                )
                if not action:
                    action = config.get_open_app(
                        file.rsplit('.', 1)[-1].lower()
                    )
                    if not action:
                        raise SystemExit(
                            f"{sys.argv[0]}: unknown file extension: {file}",
                        )
            self._spawn(action, file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
