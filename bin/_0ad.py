#!/usr/bin/env python3
"""
Sandbox for "0ad" launcher
"""
# pylint: disable=invalid-name

import os
import signal
import sys
from pathlib import Path

import network_mod
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
        command = network_mod.Sandbox("0ad", errors='stop')
        command.set_args(sys.argv[1:])
        if not Path(f'{command.get_file()}.py').is_file():
            configs = [
                '/dev/dri',
                f'/run/user/{os.getuid()}/pulse',
                Path(Path.home(), '.config/0ad'),
            ]
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                command.set_args(sys.argv[2:])
                configs.append('net')
            command.sandbox(configs)

        subtask_mod.Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
