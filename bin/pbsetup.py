#!/usr/bin/env python3
"""
PUNK BUSTER SETUP launcher
"""

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
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_pbsetup(self) -> command_mod.Command:
        """
        Return pbsetup Command class object.
        """
        return self._pbsetup

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._pbsetup = command_mod.Command('pbsetup.run', errors='ignore')
        if not self._pbsetup.is_found():
            self._pbsetup = command_mod.Command('pbsetup', errors='stop')
        self._pbsetup.set_args(args[1:])
        self._pattern = ': wrong ELF class:|: Gtk-WARNING '


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

        subtask_mod.Task(
            options.get_pbsetup().get_cmdline()).run(
                pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
