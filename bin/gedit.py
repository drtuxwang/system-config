#!/usr/bin/env python3
"""
Wrapper for "gedit" command
"""

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
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_gedit(self) -> command_mod.Command:
        """
        Return gedit Command class object.
        """
        return self._gedit

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._gedit = command_mod.Command('gedit', errors='stop')
        self._gedit.set_args(args[1:])
        self._pattern = (
            '^$|$HOME/.gnome|FAMOpen| DEBUG: |GEDIT_IS_PLUGIN|'
            'IPP request failed|egg_recent_model_|g_bookmark_file_get_size:|'
            'recently-used.xbel|Could not load theme'
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

        subtask_mod.Background(options.get_gedit().get_cmdline(
            )).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
