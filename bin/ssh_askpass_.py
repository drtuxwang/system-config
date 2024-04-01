#!/usr/bin/env python3
"""
Wrapper for "ssh-askpass" command
"""

import signal
import sys

from command_mod import Command
from subtask_mod import Task


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
        command = Command('ssh-askpass', errors='stop')
        cmdline = command.get_cmdline() + sys.argv[1:]

        Task(cmdline).run(pattern='dbind-WARNING|^$')

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
