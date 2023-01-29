#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE desktop file manager
"""

import signal
import sys

import command_mod
import desktop_mod
import subtask_mod

PROGRAMS = {
    'cinnamon': ['nemo'],
    'gnome': ['nautilus'],
    'kde': ['dolphin'],
    'mate': ['caja'],
    'xfce': ['thunar'],
}
GENERIC = ['xterm']


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

    @staticmethod
    def run() -> int:
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
        subtask_mod.Daemon(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
