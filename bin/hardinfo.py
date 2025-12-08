#!/usr/bin/env python3
"""
Wrapper for "hardinfo" command
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from file_mod import FileUtil
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

        # Send ".hardinfo" to tmpfs
        newhome = FileUtil.tmpdir(Path('.cache', 'hardinfo'))
        os.environ['HOME'] = newhome

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        hardinfo = Command('hardinfo2', errors='ignore')
        if not hardinfo.is_found():
            hardinfo = Command(Path('bin', 'hardinfo'), errors='stop')
        hardinfo.set_args(sys.argv[1:])

        pattern = "^$|dbind-WARNING|Gdk-CRITICAL|GLib-CRITICAL"
        Background(hardinfo.get_cmdline()).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
