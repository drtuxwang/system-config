#!/usr/bin/env python3
"""
Wrapper for "xournal" command
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
        xournal = command_mod.Command(
            'xournal',
            args=sys.argv[1:],
            errors='stop'
        )
        pattern = ('^$|: Gtk-WARNING ')

        subtask_mod.Background(xournal.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
