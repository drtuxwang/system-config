#!/usr/bin/env python3
"""
Uncompress a file in ZST format.
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

    def get_bzstd(self) -> Command:
        """
        Return bzstd Command class object.
        """
        return self._bzstd

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Uncompress a file in ZST format.",
        )

        parser.add_argument(
            '-test',
            dest='test_flag',
            action='store_true',
            help="Test archive data only.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.zst',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._bzstd = Command('zstd', errors='stop')

        if self._args.test_flag:
            self._bzstd.set_args(['-t'])
        else:
            self._bzstd.set_args(['-d'])
        self._bzstd.extend_args(self._args.archives)


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

        Exec(options.get_bzstd().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
