#!/usr/bin/env python3
"""
Wrapper for generic command (removes wrapper directory from PATH)
"""

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

    @staticmethod
    def run():
        """
        Start program
        """
        paths = os.environ['PATH'].split(os.path.pathsep)
        paths.remove(os.path.dirname(sys.argv[0]))
        os.environ['PATH'] = os.path.pathsep.join(paths)

        name = os.path.basename(sys.argv[0]).replace('.py', '')

        command = command_mod.Command(name, errors='stop')
        command.set_args(sys.argv[1:])
        subtask_mod.Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
