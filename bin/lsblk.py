#!/usr/bin/env python3
"""
Wrapper for "lsblk" command (sensible defaults)
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

    @staticmethod
    def run() -> None:
        """
        Start program
        """
        lsblk = Command('lsblk', errors='stop')
        if len(sys.argv) == 1:
            lsblk.set_args([
                '-o',
                'NAME,SIZE,FSTYPE,LABEL,UUID,DISC-GRAN,MOUNTPOINT',
            ])
        else:
            lsblk.set_args(sys.argv[1:])
        Exec(lsblk.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
