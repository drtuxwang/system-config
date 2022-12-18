#!/usr/bin/env python3
"""
Check PATH and return correct settings.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_path(self) -> str:
        """
        Return search path.
        """
        return self._path

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Check PATH and return correct settings.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._path = os.environ['PATH']


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

        path = []
        print()
        for directory in options.get_path().split(os.pathsep):
            if directory:
                if not Path(directory).is_dir():
                    print(f"{directory}: fail")
                elif directory in path:
                    print(f"{directory}: repeat")
                else:
                    print(f"{directory}: ok")
                    path.append(directory)
        print("\nThe correct PATH should be:")
        print(os.pathsep.join(path))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
