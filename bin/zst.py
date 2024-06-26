#!/usr/bin/env python3
"""
Compress a file in ZST format.
"""

import argparse
import signal
import sys
from typing import List

from command_mod import Command
from subtask_mod import Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_zstd(self) -> Command:
        """
        Return zstd Command class object.
        """
        return self._zstd

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Compress a file in ZST format.",
        )

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='File to compresss to "file.zst".'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._zstd = Command('zstd', errors='stop')
        self._zstd.set_args(['--ultra', '-22', '-T0'] + self._args.files)


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

        Exec(options.get_zstd().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
