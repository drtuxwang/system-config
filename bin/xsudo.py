#!/usr/bin/env python3
"""
Run sudo command in new terminal session
"""

import glob
import os
import signal
import sys

import syslib

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
        xterm = syslib.Command('xterm')
        xterm.set_flags(['-fn', '-misc-fixed-bold-r-normal--18-*-iso8859-1', '-fg', '#000000',
                         '-bg', '#ffffdd', '-cr', '#ff0000', '-geometry', '100x24', '-ut', '+sb'])
        sudo = syslib.Command('sudo')

        if len(sys.argv) > 1:
            xterm.extend_flags(['-T', 'sudo ' + xterm.args2cmd(sys.argv[1:])])
            sudo.set_args(sys.argv[1:])
        else:
            xterm.extend_flags(['-T', 'sudo su'])
            sudo.set_args(['su'])
        xterm.append_flag('-e')
        sudo.set_wrapper(xterm)

        sudo.run(mode='daemon')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
