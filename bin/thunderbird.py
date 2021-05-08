#!/usr/bin/env python3
"""
Wrapper for "thunderbird" command
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
        Return filter patern.
        """
        return self._pattern

    def get_thunderbird(self) -> command_mod.Command:
        """
        Return Thunderbird Command class object.
        """
        return self._thunderbird

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._thunderbird = command_mod.Command(
            os.path.basename(args[0]).replace('.py', ''), errors='stop')

        self._thunderbird.extend_args(args[1:])
        self._pattern = ('^$|: GLib-GObject-CRITICAL |calBackendLoader')


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

        subtask_mod.Background(options.get_thunderbird().get_cmdline()).run(
            pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
