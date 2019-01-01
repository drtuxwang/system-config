#!/usr/bin/env python3
"""
Run ssudo command in new terminal session
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'


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
        xterm = command_mod.Command('xterm', errors='stop')
        xterm.set_args([
            '-fn',
            '-misc-fixed-bold-r-normal--18-*-iso8859-1',
            '-fg',
            FG_COLOUR,
            '-bg',
            BG_COLOUR,
            '-cr',
            '#ff0000',
            '-geometry',
            '100x24',
            '-ut',
            '+sb'
        ])
        ssudo = command_mod.Command('ssudo', errors='stop')

        if len(sys.argv) > 1:
            xterm.extend_args(
                ['-T', 'ssudo ' + xterm.args2cmd(sys.argv[1:]), '-e'])
            ssudo.set_args(sys.argv[1:])
        else:
            xterm.extend_args(['-T', 'ssudo su', '-e'])
            ssudo.set_args(['su', '-'])

        subtask_mod.Exec(xterm.get_cmdline() + ssudo.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
