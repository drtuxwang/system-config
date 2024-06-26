#!/usr/bin/env python3
"""
Wrapper for "meld" command
"""

import signal
import sys
from typing import List

from command_mod import Command
from subtask_mod import Task


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

    def get_meld(self) -> Command:
        """
        Return meld Command class object.
        """
        return self._meld

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._meld = Command('meld', args=args[1:], errors='stop')
        self._pattern = (
            ': Gtk-WARNING |: GtkWarning: | self.recent_manager =| gtk.main()|'
            'accessibility bus address:|: GLib-GIO-CRITICAL|: dconf-CRITICAL|'
            '^$'
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

        task = Task(options.get_meld().get_cmdline())
        task.run(pattern=options.get_pattern())
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
