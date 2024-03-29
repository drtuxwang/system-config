#!/usr/bin/env python3
"""
Wrapper for "espeak espeak

Example:
  espeak -a128 -k30 -ven+f2 -s60 -x "Hello World"
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

    def __init__(self, args: List[str]) -> None:
        self._espeak = command_mod.Command('espeak-ng', errors='stop')
        self._espeak.set_args(args[1:])
        self._pattern = ': Connection refused'

    def get_espeak(self) -> command_mod.Command:
        """
        Return espeak Command class object.
        """
        return self._espeak

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern


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
        options = Options(sys.argv)

        task = subtask_mod.Task(options.get_espeak().get_cmdline())
        task.run(pattern=options.get_pattern())

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
