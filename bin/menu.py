#!/usr/bin/env python3
"""
Start Menu Main for launching software
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
        self._config()
        self._setenv(args)
        self._menu = syslib.Command('menu_main.tcl')

    def get_menu(self):
        """
        Return menu Command class object.
        """
        return self._menu

    def _config(self):
        if 'HOME' in os.environ:
            os.chdir(os.environ['HOME'])

    def _setenv(self, args):
        directory = os.path.dirname(os.path.abspath(args[0]))
        if 'BASE_PATH' in os.environ:
            os.environ['PATH'] = directory + os.pathsep + os.environ['BASE_PATH']
        elif directory not in os.environ['PATH'].split(os.pathsep):
            os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']


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
            options.get_menu().run(filter='Failed to load module:', mode='background')
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
