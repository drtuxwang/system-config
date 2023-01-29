#!/usr/bin/env python3
"""
Compress a file in BZIP2 format.
"""

import argparse
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

    def get_bzip2(self) -> command_mod.Command:
        """
        Return bzip2 Command class object.
        """
        return self._bzip2

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Compress a file in BZIP2 format.",
        )

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='File to compresss to "file.bz2".',
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._bzip2 = command_mod.Command('bzip2', errors='stop')
        self._bzip2.set_args(['-9', '-k'] + self._args.files)


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

        subtask_mod.Exec(options.get_bzip2().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
