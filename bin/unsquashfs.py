#!/usr/bin/env python3
"""
Unpack a compressed archive in SQUASHFS format.
"""

import argparse
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

    def get_archiver(self) -> command_mod.Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self) -> List[str]:
        """
        Return list of archives files.
        """
        return self._args.archives

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in UNSQUASHFS format.",
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
            metavar='file.squashfs',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._archiver = command_mod.Command('unsquashfs', errors='stop')

        if len(args) > 1 and args[1].startswith('-') and args[1] != '-v':
            subtask_mod.Exec(self._archiver.get_cmdline() + args[1:]).run()

        self._parse_args(args[1:])

        if self._args.view_flag:
            self._archiver.set_args(['-l'])
        else:
            self._archiver.set_args(['-f', '-d', '.'])


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

        os.umask(0o022)
        archiver = options.get_archiver()

        for archive in options.get_archives():
            task = subtask_mod.Task(archiver.get_cmdline() + [archive])
            task.run()
            if task.get_exitcode():
                print(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                    file=sys.stderr
                )
                raise SystemExit(task.get_exitcode())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
