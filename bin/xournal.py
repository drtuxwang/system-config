#!/usr/bin/env python3
"""
Wrapper for "xournalpp" launcher
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command, Platform
from subtask_mod import Background


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
        pathextra = (
            ['/Applications/Xournal++.app/Contents/MacOS']
            if Platform.get_system() == 'macos'
            else []
        )
        xournal = Command(
            'xournalpp',
            pathextra=pathextra,
            args=sys.argv[1:],
            errors='stop',
        )

        pattern = (
            '^$|: Gtk-WARNING|: dbind-WARNING|^ALSA|^[jJ]ack|^Cannot connect|'
            ': TEXTDOMAINDIR|: Plugin| does not exist|: No such file|'
            r'No device found|not finding devices!| defaults\['
        )
        Background(xournal.get_cmdline()).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
