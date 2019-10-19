#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen snapshot
"""

import glob
import os
import signal
import sys

import command_mod
import desktop_mod
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
        if desktop == 'gnome':
            xsnap = command_mod.Command(
                'gnome-screenshot',
                flags=['--interactive'],
                errors='stop'
            )
        elif desktop == 'kde':
            xsnap = command_mod.Command('ksnapshot', errors='stop')
        elif desktop == 'xfce':
            xsnap = command_mod.Command('xfce4-screenshooter', errors='stop')
        else:
            xsnap = command_mod.Command('true', errors='stop')
        xsnap.set_args(sys.argv[1:])

        subtask_mod.Exec(xsnap.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
