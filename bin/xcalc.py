#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE calculator
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command, CommandFile
from desktop_mod import Desktop
from subtask_mod import Exec

PROGRAMS = {
    'cinnamon': ['gnome-calculator'],
    'gnome': ['gnome-calculator'],
    'kde': ['kcalc'],
    'macos': ['/System/Applications/Calculator.app/Contents/MacOS/Calculator'],
    'mate': ['mate-calc'],
}
GENERIC = ['xcalc']


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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        desktop = Desktop.detect()
        cmdline = PROGRAMS.get(desktop, GENERIC)
        command: Command
        if Path(cmdline[0]).is_file():
            command = CommandFile(cmdline[0], errors='ignore')
        else:
            command = Command(cmdline[0], errors='ignore')

        if not command.is_found():
            cmdline = GENERIC
            command = Command(cmdline[0], errors='stop')

        command.set_args(cmdline[1:] + sys.argv[1:])
        Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
