#!/usr/bin/env python3
"""
Run "top" in xterm window
"""

import signal
import sys

from command_mod import Command
from subtask_mod import Daemon

TEXT_FONT = '*-fixed-bold-*-13-*-iso10646-*'
FG_COLOUR = '#000000'
BG_COLOUR = '#F5F5DC'
CR_COLOUR = '#FFAAFF'


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

    def run(self) -> int:
        """
        Start program
        """
        xterm = Command('xterm', errors='stop')
        xterm.set_args([
            '-fn',
            TEXT_FONT,
            '-fg',
            FG_COLOUR,
            '-bg',
            BG_COLOUR,
            '-cr',
            CR_COLOUR,
            '-geometry',
            '100x40+120+20',
            '-ut',
            '+sb',
            '-e',
            'top',
        ])
        Daemon(xterm.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
