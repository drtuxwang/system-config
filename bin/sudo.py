#!/usr/bin/env python3
"""
Wrapper for "sudo" command
"""

import glob
import os
import signal
import socket
import sys

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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        name = os.path.basename(sys.argv[0]).split('.')[0]

        command = command_mod.Command('sudo', errors='stop')
        if '-p' not in sys.argv:
            hostname = socket.gethostname().split('.')[0].lower()
            username = os.getlogin()
            command.set_args([
                '-p',
                '[{0:s}] password for {1:s}@{2:s}: '.format(
                    name,
                    username,
                    hostname,
                ),
            ])
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
