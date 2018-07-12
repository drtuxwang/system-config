#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE calculator
"""

import signal
import sys

import command_mod
import desktop_mod
import subtask_mod

if sys.version_info < (3, 4) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.4, < 4.0).")


class Main(object):
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
        desktop = desktop_mod.Desktop.detect()
        if desktop == 'gnome':
            xcalc = command_mod.Command('gcalctool', errors='ignore')
            if not xcalc.is_found():
                xcalc = command_mod.Command('xcalc', errors='stop')
        elif desktop == 'kde':
            xcalc = command_mod.Command('kcalc', errors='ignore')
            if not xcalc.is_found():
                xcalc = command_mod.Command('xcalc', errors='stop')
        else:
            xcalc = command_mod.Command('xcalc', errors='stop')

        subtask_mod.Exec(xcalc.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
