#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE calculator
"""

import signal
import sys

import ck_desktop
import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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
        desktop = ck_desktop.Desktop().detect()
        if desktop == 'gnome':
            xcalc = syslib.Command('gcalctool', check=False)
            if not xcalc.is_found():
                xcalc = syslib.Command('xcalc')
        elif desktop == 'kde':
            xcalc = syslib.Command('kcalc', check=False)
            if not xcalc.is_found():
                xcalc = syslib.Command('xcalc')
        else:
            xcalc = syslib.Command('xcalc')

        xcalc.run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
