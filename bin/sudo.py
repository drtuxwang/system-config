#!/usr/bin/env python3
"""
Wrapper for "sudo" command
"""

import getpass
import glob
import os
import signal
import socket
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def run():
        """
        Start program
        """
        command = command_mod.Command('sudo', errors='stop')
        if '-p' not in sys.argv:
            hostname = socket.gethostname().split('.')[0].lower()
            username = getpass.getuser()
            command.set_args([
                '-p',
                '[sudo] password for {0:s}@{1:s}: '.format(hostname, username)
            ])
        command.extend_args(sys.argv[1:])
        task = subtask_mod.Task(command.get_cmdline())
        task.run()

        # Remove sudo credentials
        command.set_args(['-k'])
        subtask_mod.Batch(command.get_cmdline()).run()

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
