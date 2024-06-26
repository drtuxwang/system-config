#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen snapshot
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command, CommandFile
from desktop_mod import Desktop
from subtask_mod import Task

PROGRAMS = {
    'cinnamon': ['gnome-screenshot', '--interactive'],
    'gnome': ['gnome-screenshot', '--interactive'],
    'kde': ['ksnapshot'],
    'macos': [
        '/System/Applications/Utilities/Screenshot.app/'
        'Contents/MacOS/Screenshot',
    ],
    'mate': ['mate-screenshot'],
    'xfce': ['xfce4-screenshooter'],
}
GENERIC = ['true']


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
        command = (
            CommandFile(cmdline[0], errors='ignore')
            if Path(cmdline[0]).is_file()
            else Command(cmdline[0], errors='ignore')
        )

        if not command.is_found():
            cmdline = GENERIC
            command = Command(cmdline[0], errors='stop')
        command.set_args(cmdline[1:] + sys.argv[1:])

        pattern = (
            '^$|dbind-WARNING|Gtk-WARNING|Gtk-CRITICAL|GLib-GObject-CRITICAL'
        )
        task = Task(command.get_cmdline())
        task.run(pattern=pattern)

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
