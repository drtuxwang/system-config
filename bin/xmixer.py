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

DEFAULT = ['pavucontrol']
PROGRAMS = {
    'cinnamon': ['cinnamon-settings', 'sound'],
    'gnome': ['gnome-control-center', 'sound'],
    'kde': ['kmix'],
    'mate': ['mate-volume-control'],
    'xfce': ['xfce4-mixer'],
}
GENERIC = ['alsamixer']


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
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
    def run() -> int:
        """
        Start program
        """
        cmdline = DEFAULT
        command = command_mod.Command(cmdline[0], errors='ignore')

        if not command.is_found():
            desktop = desktop_mod.Desktop.detect()
            cmdline = PROGRAMS.get(desktop, GENERIC)
            command = command_mod.Command(cmdline[0], errors='ignore')

            if not command.is_found():
                cmdline = GENERIC
                command = command_mod.Command(cmdline[0], errors='stop')
                command.set_args(cmdline[1:] + sys.argv[1:])

        command.set_args(cmdline[1:] + sys.argv[1:])
        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
