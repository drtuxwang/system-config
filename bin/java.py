#!/usr/bin/env python3
"""
JAVA launcher
"""

import glob
import os
import shutil
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
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

        # Send ".java" to tmpfs
        tmpdir = file_mod.FileUtil.tmpdir(os.path.join('.cache', 'java'))
        directory = os.path.join(os.environ.get('HOME'), '.java')
        if not os.path.islink(directory):
            try:
                shutil.rmtree(directory)
            except OSError:
                pass
            try:
                os.symlink(tmpdir, directory)
            except OSError:
                pass

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        java = command_mod.Command(os.path.join('bin', 'java'), errors='stop')
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
