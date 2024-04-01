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

from command_mod import Command
from subtask_mod import ExecutableCallError, Task


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
        sudo = Command('sudo', errors='stop')
        if '-p' not in sys.argv:
            hostname = socket.gethostname().split('.')[0].lower()
            username = getpass.getuser()
            sudo.set_args(
                ['-p', f'[sudo] password for {username}@{hostname}: ']
            )
        if len(sys.argv) > 1:
            if sys.argv[1:] == ['su']:  # Workaround hanging
                sys.argv[1] = '-s'
            elif not sys.argv[1].startswith('-'):
                command = Command(sys.argv[1], errors='ignore')
                if command.is_found():
                    sys.argv[1] = command.get_file()
            sudo.extend_args(sys.argv[1:])

        # Run and remove sudo credentials
        task = Task(sudo.get_cmdline())
        try:
            task.run()
        except ExecutableCallError:
            pass
        sudo.set_args(['-k'])
        Task(sudo.get_cmdline()).run()

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
