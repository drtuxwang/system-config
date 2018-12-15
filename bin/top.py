#!/usr/bin/env python3
"""
Show dynamic real-time status of a running system
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Main:
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
        sys.exit(0)

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
    def _get_top():
        if os.name == 'posix' and os.uname()[0] == 'SunOS':
            if os.path.isfile('/bin/prstat'):
                return command_mod.CommandFile('/bin/prstat', args=['10'])
            return command_mod.Command('prstat', args=['10'], errors='stop')

        return command_mod.Command('top', errors='stop')

    @classmethod
    def run(cls):
        """
        Start program
        """
        top = cls._get_top()
        top.extend_args(sys.argv[1:])

        subtask_mod.Exec(top.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
