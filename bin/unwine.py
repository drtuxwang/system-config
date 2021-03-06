#!/usr/bin/env python3
"""
Shuts down WINE and all Windows applications
"""

import signal
import sys

import command_mod
import subtask_mod


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def run():
        """
        Start program
        """
        wineserver = command_mod.Command(
            'wineserver', args=['-k'], errors='stop')

        subtask_mod.Task(wineserver.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
