#!/usr/bin/env python3
"""
View files using default application
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple

from command_mod import Command, CommandFile
from config_mod import Config
from subtask_mod import Daemon, Task


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
    def _get_program(command: List[str]) -> Command:
        path = Path(sys.argv[0]).with_name(command[0])
        if path.is_file():
            return CommandFile(path)
        return Command(command[0], errors='stop')

    @classmethod
    def _spawn(cls, action: Tuple[List[str], bool], file: str) -> None:
        command, daemon = action
        if not command:
            raise SystemExit(f"{sys.argv[0]}: cannot find action: {file}")
        program = cls._get_program(command)
        program.set_args(command[1:] + [file])
        cmdline = program.get_cmdline()
        print(f"Viewing: {Command.args2cmd(cmdline)}")
        if daemon:
            Daemon(cmdline).run()
        else:
            Task(cmdline).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        config = Config()

        for path in [Path(x) for x in options.get_files()]:
            if path.is_dir():
                action = config.get_app('file_manager')
            elif str(path).split(':', 1)[0] in config.get('web_uri'):
                action = config.get_app('web_browser')
            elif not path.is_file():
                raise SystemExit(f"{sys.argv[0]}: cannot find file: {path}")
            else:
                action = config.get_view_app(path.suffix.lower())
                if not action:
                    action = config.get_open_app(path.suffix.lower())
                    if not action:
                        raise SystemExit(
                            f"{sys.argv[0]}: unknown file extension: {path}",
                        )
            self._spawn(action, str(path))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
