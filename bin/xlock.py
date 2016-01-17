#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen lock
"""

import glob
import os
import signal
import sys
import time

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
        self._desktop = ck_desktop.Desktop().detect()
        self._xlock = syslib.Command('light-locker-command', flags=['--lock'], check=False)
        if self._xlock.is_found():
            if not syslib.Task().haspname('light-locker'):
                syslib.Command('light-locker').run(mode='daemon')
                time.sleep(1)
        elif self._desktop == 'gnome':
            self._xlock = syslib.Command('gnome-screensaver-command', flags=['--lock'])
            if not syslib.Task().haspname('gnome-screensaver'):
                syslib.Command('gnome-screensaver').run()
        elif self._desktop == 'kde':
            self._xlock = syslib.Command(
                'qdbus', flags=['org.freedesktop.ScreenSaver', '/ScreenSaver', 'Lock'])
        elif self._desktop == 'xfce':
            self._xlock = syslib.Command('xscreensaver-command', flags=['-lock'])
        else:
            self._xlock = syslib.Command('xlock')
            self._xlock.set_flags(['-allowroot', '+nolock', '-mode', 'blank', '-fg', 'red',
                                   '-bg', 'black', '-timeout', '10'])
        self._xlock.set_args(args[1:])
        if 'VNCDESKTOP' in os.environ:
            os.environ['DISPLAY'] = ':0'

    def get_xlock(self):
        """
        Return xlock Command class object.
        """
        return self._xlock


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
            options.get_xlock().run(mode='background')
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
