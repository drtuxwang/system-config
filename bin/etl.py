#!/usr/bin/env python3
"""
WOLFENSTEIN ENEMY TERRITORY LEGACY game launcher
"""

import glob
import os
import signal
import sys

import command_mod
import file_mod
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
        etl = command_mod.Command('etl', errors='stop')
        etl.set_args(sys.argv[1:])
        os.chdir(os.path.dirname(etl.get_file()))

        logfile = os.path.join(file_mod.FileUtil.tmpdir(), 'etl.log')
        subtask_mod.Daemon(etl.get_cmdline()).run(file=logfile)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
