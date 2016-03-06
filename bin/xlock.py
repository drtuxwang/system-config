#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen lock
"""

import glob
import os
import signal
import sys
import time

import desktop_mod
import syslib
import task_mod

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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run():
        """
        Start program
        """
        desktop = desktop_mod.Desktop.detect()
        xlock = syslib.Command('light-locker-command', flags=['--lock'], check=False)
        if xlock.is_found():
            if not task_mod.Tasks.factory().haspname('light-locker'):
                syslib.Command('light-locker').run(mode='daemon')
                time.sleep(1)
        elif desktop == 'gnome':
            xlock = syslib.Command('gnome-screensaver-command', flags=['--lock'])
            if not task_mod.Tasks.factory().haspname('gnome-screensaver'):
                syslib.Command('gnome-screensaver').run()
        elif desktop == 'kde':
            xlock = syslib.Command(
                'qdbus', flags=['org.freedesktop.ScreenSaver', '/ScreenSaver', 'Lock'])
        elif desktop == 'xfce':
            xlock = syslib.Command('xscreensaver-command', flags=['-lock'])
        else:
            xlock = syslib.Command('xlock')
            xlock.set_flags(['-allowroot', '+nolock', '-mode', 'blank', '-fg', 'red',
                             '-bg', 'black', '-timeout', '10'])
        xlock.set_args(sys.argv[1:])
        if 'VNCDESKTOP' in os.environ:
            os.environ['DISPLAY'] = ':0'

        xlock.run(mode='background')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
