#!/usr/bin/env python3
"""
Wrapper for "sudo" command
"""

import getpass
import os
import signal
import socket
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
        name = Path(sys.argv[0]).name.split('.')[0]

        command = command_mod.Command('sudo', errors='stop')
        if '-p' not in sys.argv:
            hostname = socket.gethostname().split('.')[0].lower()
            username = getpass.getuser()
            command.set_args([
                '-p',
                f'[{name}] password for {username}@{hostname}: ',
            ])
        if sys.argv[1:] == ['su']:  # Workaround hanging
            command.extend_args(['-s'])
        else:
            command.extend_args(sys.argv[1:])

        if name == 'name':
            subtask_mod.Exec(command.get_cmdline()).run()

        # Remove sudo credentials after execution
        task = subtask_mod.Task(command.get_cmdline())
        try:
            task.run()
        except subtask_mod.ExecutableCallError:
            pass
        command.set_args(['-k'])
        subtask_mod.Task(command.get_cmdline()).run()

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
