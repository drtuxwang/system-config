#!/usr/bin/env python3
"""
Wrapper for "cal" command
"""

import signal
import sys

from command_mod import Command
from subtask_mod import Exec


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

    @classmethod
    def run(cls) -> None:
        """
        Start program
        """
        command = Command('ncal', errors='ignore')
        if command.is_found():
            command.extend_args(['-b', '-M'])
        else:
            command = Command('cal', errors='stop')
        command.extend_args(sys.argv[1:])

        Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
