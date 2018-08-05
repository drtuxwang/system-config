#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE audio mixer
"""

import glob
import os
import signal
import sys

import command_mod
import desktop_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


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
        xmixer = command_mod.Command('pavucontrol', errors='ignore')
        if not xmixer.is_found():
            desktop = desktop_mod.Desktop.detect()
            if desktop == 'gnome':
                xmixer = command_mod.Command(
                    'gnome-volume-control',
                    errors='ignore'
                )
            elif desktop == 'kde':
                xmixer = command_mod.Command('kmix', errors='ignore')
            elif desktop == 'xfce':
                xmixer = command_mod.Command('xfce4-mixer', errors='ignore')
            if not xmixer.is_found():
                xmixer = command_mod.Command('alsamixer', errors='stop')
        xmixer.set_args(sys.argv[1:])

        subtask_mod.Exec(xmixer.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
