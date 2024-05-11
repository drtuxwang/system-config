#!/usr/bin/env python3
"""
Wrapper for Visual Studio Code command
"""

import os
import signal
import sys
from pathlib import Path
from typing import Any

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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        code = Command('code', errors='ignore')
        if not code.is_found():
            if Platform.get_system() == 'macos':
                code = Command('Electron', pathextra=[
                    '/Applications/Visual Studio Code.app/Contents/MacOS'
                ], errors='ignore')
                if not code.is_found():
                    Command('code', errors='stop')
        code.set_args(sys.argv[1:])

        pattern = r"^$|GLib-GIO-WARNING|\[main "
        Background(code.get_cmdline()).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
