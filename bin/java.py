#!/usr/bin/env python3
"""
JAVA launcher
"""

import glob
import os
import shutil
import signal
import sys
from pathlib import Path

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

        # Send ".java" to tmpfs
        tmpdir = file_mod.FileUtil.tmpdir(Path('.cache', 'java'))
        path = Path(Path.home(), '.java')
        if not path.is_symlink():
            try:
                shutil.rmtree(path)
            except OSError:
                pass
            try:
                path.symlink_to(tmpdir)
            except OSError:
                pass

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        java = command_mod.Command(Path('bin', 'java'), errors='stop')
        if len(sys.argv) > 1:
            if sys.argv[1].endswith('.jar'):
                java.set_args(['-jar'])
        java.extend_args(sys.argv[1:])

        subtask_mod.Exec(java.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
