#!/usr/bin/env python3
"""
Wrapper for "mousepad" command
"""

import signal
import sys
from typing import List

from command_mod import Command
from subtask_mod import Background


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_mousepad(self) -> Command:
        """
        Return mousepad Command class object.
        """
        return self._mousepad

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._mousepad = Command('mousepad', errors='stop')
        self._mousepad.set_args(args[1:])
        self._pattern = (
            '^$|recently-used.xbel|: Error retrieving accessibility bus|'
            ': GLib-CRITICAL |: GtkSourceView-CRITICAL|: Gtk-WARNING |'
            ': WARNING '
        )


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

        Background(
            options.get_mousepad().get_cmdline()
        ).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
