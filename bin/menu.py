#!/usr/bin/env python3
"""
Start Menu Main for launching software
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_menu(self):
        """
        Return menu Command class object.
        """
        return self._menu

    @staticmethod
    def _config():
        if 'HOME' in os.environ:
            os.chdir(os.environ['HOME'])

    @staticmethod
    def _setenv(args):
        directory = os.path.dirname(os.path.abspath(args[0]))
        if 'BASE_PATH' in os.environ:
            os.environ['PATH'] = directory + os.pathsep + os.environ['BASE_PATH']
        elif directory not in os.environ['PATH'].split(os.pathsep):
            os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']

    def parse(self, args):
        """
        Parse arguments
        """
        self._config()
        self._setenv(args)
        self._menu = command_mod.Command('menu_main.tcl', errors='stop')


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
        options = Options()

        subtask_mod.Background(options.get_menu().get_cmdline()).run(
            pattern='Failed to load module:')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
