#!/usr/bin/env python3
"""
JAVA launcher
"""

import getpass
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod


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

        # Send ".java" to tmpfs
        tmpdir = os.path.join('/tmp', getpass.getuser(), '.cache', 'java')
        try:
            os.makedirs(tmpdir)
        except FileExistsError:
            pass
        os.chmod(tmpdir, int('700', 8))
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
    def run():
        """
        Start program
        """
        java = command_mod.Command(os.path.join('bin', 'java'), errors='stop')
        if len(sys.argv) > 1:
            if sys.argv[1].endswith('.jar'):
                java.set_args(['-jar'])
        java.extend_args(sys.argv[1:])

        subtask_mod.Exec(java.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
