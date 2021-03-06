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

PROGRAMS = {
    'cinnamon': ['gedit'],
    'gnome': ['gedit'],
    'kde': ['kate'],
    'mate': ['pluma'],
    'xfce': ['mousepad'],
}
GENERIC = ['vi']


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
        cmdline = PROGRAMS.get(desktop, GENERIC)
        command = command_mod.Command(cmdline[0], errors='ignore')

        if not command.is_found():
            cmdline = GENERIC
            command = command_mod.Command(cmdline[0], errors='stop')

        command.set_args(cmdline[1:] + sys.argv[1:])
        subtask_mod.Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
