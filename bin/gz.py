#!/usr/bin/env python3
"""
Compress a file in GZIP format.
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

    def get_gzip(self) -> command_mod.Command:
        """
        Return gzip Command class object.
        """
        return self._gzip

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Compress a file in GZIP format.',
        )

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='File to compresss to "file.gz".'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gzip = command_mod.Command('gzip', errors='stop')
        self._gzip.set_args(['-9', '-k'] + self._args.files)


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

        subtask_mod.Exec(options.get_gzip().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
