#!/usr/bin/env python3
"""
HARDINFO launcher
"""

import getpass
import glob
import os
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

        # Send ".hardinfo" to tmpfs
        tmpdir = os.path.join('/tmp', getpass.getuser())
        directory = os.path.join(tmpdir, '.cache')
        try:
            os.makedirs(directory)
        except FileExistsError:
            pass
        os.chmod(tmpdir, int('700', 8))
        os.environ['HOME'] = tmpdir

    @staticmethod
    def run():
        """
        Start program
        """
        hardinfo = command_mod.Command(
            os.path.join('bin', 'hardinfo'),
            errors='stop',
            args=sys.argv[1:],
        )

        subtask_mod.Exec(hardinfo.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
