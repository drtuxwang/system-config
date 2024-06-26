#!/usr/bin/env python3
"""
Trace network route to host
"""

import os
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
        sys.exit(0)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def _is_windows() -> bool:
        """
        Return True if running on Windows.
        """
        if os.name == 'posix':
            if os.uname()[0].startswith('cygwin'):
                return True
        elif os.name == 'nt':
            return True

        return False

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        if cls._is_windows():
            command = Command('tracert.exe', errors='stop')
        else:
            command = Command('tcptraceroute', errors='ignore')
            if not command.is_found():
                command = Command(
                    'traceroute',
                    pathextra=['/usr/sbin', '/usr/etc'],
                    errors='stop'
                )
        Exec(command.get_cmdline() + sys.argv[1:]).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
