#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE graphical editor
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
import desktop_mod
import subtask_mod

PROGRAMS = {
    'cinnamon': ['gedit'],
    'gnome': ['gedit'],
    'kde': ['kate'],
    'macos': ['/System/Applications/TextEdit.app/Contents/MacOS/TextEdit'],
    'mate': ['pluma'],
    'xfce': ['mousepad'],
}
GENERIC = ['vi']


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
        desktop = desktop_mod.Desktop.detect()
        cmdline = PROGRAMS.get(desktop, GENERIC)
        command: command_mod.Command
        if Path(cmdline[0]).is_file():
            command = command_mod.CommandFile(cmdline[0], errors='ignore')
        else:
            command = command_mod.Command(cmdline[0], errors='ignore')

        if not command.is_found():
            cmdline = GENERIC
            command = command_mod.Command(cmdline[0], errors='stop')

        command.set_args(cmdline[1:] + sys.argv[1:])
        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
