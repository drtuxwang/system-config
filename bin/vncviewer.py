#!/usr/bin/env python3
"""
Wrapper for "vncviewer" command
"""

import signal
import sys

from command_mod import Command
from subtask_mod import Daemon, Exec


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
        vncviewer = Command('vncviewer', args=sys.argv[1:], errors='stop')
        if sys.argv[-1] in ('--help', '--version'):
            Exec(vncviewer.get_cmdline()).run()
        else:
            Daemon(vncviewer.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
