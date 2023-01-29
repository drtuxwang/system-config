#!/usr/bin/env python3
"""
Wrapper for "top" command
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
import subtask_mod


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
        sys.exit(0)

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
    def _get_top() -> command_mod.Command:
        if os.name == 'posix' and os.uname()[0] == 'SunOS':
            if Path('/bin/prstat').is_file():
                return command_mod.CommandFile('/bin/prstat', args=['10'])
            return command_mod.Command('prstat', args=['10'], errors='stop')

        return command_mod.Command('top', errors='stop')

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        top = cls._get_top()
        top.extend_args(sys.argv[1:])

        subtask_mod.Exec(top.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
