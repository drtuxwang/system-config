#!/usr/bin/env python3
"""
Wrapper for "grpcurl" command
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
import subtask_mod

VERBOSE_SIZE = 134217728


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

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        command = command_mod.Command('grpcurl', errors='stop')
        if len(sys.argv) == 2 and ':' in sys.argv[1]:
            command.set_args(['--plaintext', sys.argv[1], 'describe'])
        else:
            command.set_args(sys.argv[1:])

        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
