#!/usr/bin/env python3
"""
Shutdown X-windows
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import List

import task_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_force_flag(self) -> bool:
        """
        Return force flag.
        """
        return self._args.force_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Logout from X-windows desktop.",
        )

        parser.add_argument(
            '-force',
            dest='force_flag',
            action='store_true',
            help="Force login without confirmation.",
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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._pid = 0
        if 'SESSION_MANAGER' in os.environ:
            try:
                self._pid = int(Path(os.environ['SESSION_MANAGER']).name)
            except ValueError:
                pass

        if not options.get_force_flag():
            try:
                answer = input(
                    "Do you really want to logout of X-session? (y/n) [n] "
                )
                if answer.lower() != 'y':
                    raise SystemExit(1)
            except EOFError:
                pass
            except KeyboardInterrupt:
                sys.exit(114)

        task_mod.Tasks.factory().killpids([self._pid])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
