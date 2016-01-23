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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._desktop = ck_desktop.Desktop().detect()
        if self._desktop == 'gnome':
            self._xcalc = syslib.Command('gcalctool', check=False)
            if not self._xcalc.is_found():
                self._xcalc = syslib.Command('xcalc')
        elif self._desktop == 'kde':
            self._xcalc = syslib.Command('kcalc', check=False)
            if not self._xcalc.is_found():
                self._xcalc = syslib.Command('xcalc')
        else:
            self._xcalc = syslib.Command('xcalc')

    def get_xcalc(self):
        """
        Return calculator Command class object.
        """
        return self._xcalc


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        try:
            options = Options()
            options.get_xcalc().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
