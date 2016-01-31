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
        xmixer = syslib.Command('pavucontrol', check=False)
        if not xmixer.is_found():
            desktop = ck_desktop.Desktop().detect()
            if desktop == 'gnome':
                xmixer = syslib.Command('gnome-volume-control', check=False)
            elif desktop == 'kde':
                xmixer = syslib.Command('kmix', check=False)
            elif desktop == 'xfce':
                xmixer = syslib.Command('xfce4-mixer', check=False)
            if not xmixer.is_found():
                xmixer = syslib.Command('alsamixer')
        xmixer.set_args(sys.argv[1:])

        xmixer.run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
