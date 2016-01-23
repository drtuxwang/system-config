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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        xterm = syslib.Command('xterm')
        xterm.set_flags(['-fn', '-misc-fixed-bold-r-normal--18-*-iso8859-1', '-fg', '#000000',
                         '-bg', '#ffffdd', '-cr', '#ff0000', '-geometry', '100x24', '-ut', '+sb'])
        self._command = syslib.Command('sudo')

        if len(args) > 1:
            xterm.extend_flags(['-T', 'sudo ' + xterm.args2cmd(args[1:])])
            self._command.set_args(args[1:])
        else:
            xterm.extend_flags(['-T', 'sudo su'])
            self._command.set_args(['su'])

        xterm.append_flag('-e')
        self._command.set_wrapper(xterm)

    def get_command(self):
        """
        Return Command class object.
        """
        return self._command


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            options.get_command().run(mode='daemon')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
