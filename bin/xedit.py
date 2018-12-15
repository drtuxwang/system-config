#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE graphical editor
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
            xedit = command_mod.Command('gedit', errors='stop')
        elif desktop == 'kde':
            xedit = command_mod.Command('kate', errors='stop')
        elif desktop == 'xfce':
            xedit = command_mod.Command('mousepad', errors='stop')
        else:
            xedit = command_mod.Command('vi', errors='stop')
        xedit.set_args(sys.argv[1:])

        subtask_mod.Exec(xedit.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
