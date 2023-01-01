#!/usr/bin/env python3
"""
Unpack a compressed archive using suitable tool.",
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

    def get_archives(self) -> List[str]:
        """
        Return list of archive files.
        """
        return self._args.archives

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive using suitable tool.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='archive',
            help="Archive file.",
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        view_args = ['-v'] if options.get_view_flag() else []
        os.umask(0o022)

        for file in options.get_archives():
            name = Path(file).name
            args = view_args + [file]
            if name.endswith('.ace'):
                command = command_mod.Command('unace', errors='stop')
            elif name.endswith('.deb'):
                command = command_mod.Command('undeb', errors='stop')
            elif name.endswith('.gpg'):
                command = command_mod.Command('ungpg', errors='stop')
            elif name.startswith('initr'):
                command = command_mod.Command('uninitrd', errors='stop')
            elif name.endswith('.pdf'):
                command = command_mod.Command('unpdf', errors='stop')
            elif name.endswith('.pyc'):
                command = command_mod.Command('unpyc', errors='stop')
                args = [file]
            elif name.endswith('.sqlite'):
                command = command_mod.Command('unsqlite', errors='stop')
                args = [file]
            elif name.endswith('.squashfs'):
                command = command_mod.Command('unsquashfs', errors='stop')
            elif name.endswith((
                '.tar',
                '.tar.gz',
                '.tar.bz2',
                '.tar.zst',
                '.tar.lzma',
                '.tar.xz',
                '.tar.zst',
                '.tar.lzma',
                '.tar.xz',
                '.tar.7z',
                '.tgz',
                '.tbz',
                '.tzs',
                '.tzst',
                '.tlz',
                '.txz',
                '.t7z',
            )):
                command = command_mod.Command('untar', errors='stop')
            else:
                command = command_mod.Command('un7z', errors='stop')
            cmdline = command.get_cmdline() + args
            print(f"\nRunning: {command.args2cmd(cmdline)}")
            task = subtask_mod.Task(cmdline)
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
