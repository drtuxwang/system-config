#!/usr/bin/env python3
"""
Sandbox for "hearts" launcher
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Task


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
    def run() -> None:
        """
        Start program
        """
        name = Path(sys.argv[0]).stem

        hearts = Sandbox(name, errors='stop')
        hearts.set_args(sys.argv[1:])

        if not Path(f'{hearts.get_file()}.py').is_file():
            configs = [
                '/dev/dri',
                '/dev/shm',
                f'/run/user/{os.getuid()}/pulse',
            ]
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                hearts.set_args(sys.argv[2:])
                configs.append('net')
            hearts.sandbox(configs)

        pattern = 'deprecation:'
        Task(hearts.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
