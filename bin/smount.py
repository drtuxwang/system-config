#!/usr/bin/env python3
"""
Securely mount a file system using SSH protocol.
"""

import argparse
import signal
import sys
from typing import List

from command_mod import Command
from subtask_mod import Batch, Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_sshfs(self) -> Command:
        """
        Return sshfs Command class object.
        """
        return self._sshfs

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Securely mount a file system using SSH protocol.",
        )

        parser.add_argument(
            'remote',
            nargs=1,
            metavar='user@host:/remotepath',
            help="Remote directory.",
        )
        parser.add_argument(
            'local',
            nargs=1,
            metavar='user@host:/localpath',
            help="Local directory.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if len(args) == 1:
            mount = Command('mount', errors='stop')
            task = Batch(mount.get_cmdline())
            task.run(pattern='type fuse.sshfs ')
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            for line in task.get_output():
                print(line)
            raise SystemExit(0)

        self._parse_args(args[1:])

        self._sshfs = Command('sshfs', errors='stop')
        self._sshfs.set_args([
            '-o',
            'noatime,allow_root',
        ] + self._args.remote + self._args.local)


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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        Exec(options.get_sshfs().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
