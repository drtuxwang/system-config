#!/usr/bin/env python3
"""
Wrapper for "traceroute" command
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
    def _is_windows():
        """
        Return True if running on Windows.
        """
        if os.name == 'posix':
            if os.uname()[0].startswith('cygwin'):
                return True
        elif os.name == 'nt':
            return True

        return False

    @classmethod
    def run(cls):
        """
        Start program
        """
        if cls._is_windows():
            traceroute = command_mod.Command('tracert.exe', errors='stop')
        else:
            traceroute = command_mod.Command(
                'traceroute',
                pathextra=['/usr/sbin', '/usr/etc'],
                errors='stop'
            )
        traceroute.set_args(sys.argv[1:])

        subtask_mod.Exec(traceroute.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
