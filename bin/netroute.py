#!/usr/bin/env python3
"""
Trace network route to host
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod


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
            command = command_mod.Command('tracert.exe', errors='stop')
        else:
            command = command_mod.Command('tcptraceroute', errors='ignore')
            if not command.is_found():
                command = command_mod.Command(
                    'traceroute',
                    pathextra=['/usr/sbin', '/usr/etc'],
                    errors='stop'
                )
        subtask_mod.Exec(command.get_cmdline() + sys.argv[1:]).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
