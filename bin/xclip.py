#!/usr/bin/env python3
"""
Wrapper for "xclip" command
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
    def run() -> None:
        """
        Start program
        """
        if command_mod.Platform.get_system() == 'macos':
            if '-in' in sys.argv[1:]:
                xclip = command_mod.Command('pbcopy', errors='stop')
            else:
                xclip = command_mod.Command('pbpaste', errors='stop')
        else:
            xclip = command_mod.Command('xclip', errors='stop')

        subtask_mod.Exec(xclip.get_cmdline() + sys.argv[1:]).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
