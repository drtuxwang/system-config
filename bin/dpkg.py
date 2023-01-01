#!/usr/bin/env python3
"""
Wrapper for "dpkg" command (force system Python)
"""

import glob
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
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
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
        directories = os.environ['PATH'].split(os.pathsep)
        try:
            directories.remove(str(Path(sys.argv[0]).parent))
        except ValueError:
            pass
        os.environ['PATH'] = os.pathsep.join(directories)

        name = Path(sys.argv[0]).stem

        command = command_mod.Command(name, errors='stop')
        command.set_args(sys.argv[1:])
        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
