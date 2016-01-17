#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE audio mixer
"""

import glob
import os
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

    def __init__(self, args):
        self._xmixer = syslib.Command('pavucontrol', check=False)
        if not self._xmixer.is_found():
            self._desktop = ck_desktop.Desktop().detect()
            if self._desktop == 'gnome':
                self._xmixer = syslib.Command('gnome-volume-control', check=False)
            elif self._desktop == 'kde':
                self._xmixer = syslib.Command('kmix', check=False)
            elif self._desktop == 'xfce':
                self._xmixer = syslib.Command('xfce4-mixer', check=False)
            if not self._xmixer.is_found():
                self._xmixer = syslib.Command('alsamixer')
        self._xmixer.set_args(args[1:])

    def get_xmixer(self):
        """
        Return xmixer Command class object.
        """
        return self._xmixer


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            options.get_xmixer().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
