#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen snapshot
"""

import glob
import os
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
        except (syslib.SyslibError, SystemExit) as exception:
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
        desktop = ck_desktop.Desktop().detect()
        if desktop == 'gnome':
            xsnap = syslib.Command('gnome-screenshot', flags=['--interactive'])
        elif desktop == 'kde':
            xsnap = syslib.Command('ksnapshot')
        elif desktop == 'xfce':
            xsnap = syslib.Command('xfce4-screenshooter')
        else:
            xsnap = syslib.Command('true')
        xsnap.set_args(sys.argv[1:])

        xsnap.run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
