#!/usr/bin/env python3
"""
Wrapper for Nifty Host Selector 'nhs' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._nhs = syslib.Command('nhs')
        self._nhs.set_args(args[1:])
        self._config()

    def get_command(self):
        """
        Return Command class object.
        """
        return self._nhs

    def _config(self):
        if 'HOME' in os.environ:
            home = os.environ['HOME']
            if os.path.basename(home) != '.nhs':
                home = os.path.join(home, '.nhs')
                if not os.path.isdir(home):
                    try:
                        os.mkdir(home)
                    except OSError:
                        return
                os.environ['HOME'] = home


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
            options.get_command().run(mode='exec')
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
