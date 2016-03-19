#!/usr/bin/env python3
"""
Wrapper for 'eclipse' command (Ecilpse IDE for Java EE Developers)
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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
        eclipse = command_mod.Command('eclipse', errors='stop')
        if len(sys.argv) == 1:
            java = command_mod.Command(os.path.join('bin', 'java'), errors='stop')
            args = ['-vm', java.get_file(), '-vmargs', '-Xms2048m',
                    '-Xmx2048m', '-XX:PermSize=8192m', '-XX:MaxPermSize=8192m',
                    '-XX:-UseCompressedOops']
        else:
            args = sys.argv[1:]

        subtask_mod.Background(eclipse.get_cmdline() + args).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
