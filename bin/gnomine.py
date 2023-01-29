#!/usr/bin/env python3
"""
Wrapper for "gnomine" command
"""

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
        command = command_mod.Command('gnome-mines', errors='ignore')
        if not command.is_found():
            command = command_mod.Command('gnomine', errors='ignore')
            if not command.is_found():
                command = command_mod.Command('gnome-mines', errors='stop')
        command.set_args(sys.argv[1:])

        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
