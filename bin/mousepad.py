#!/usr/bin/env python3
"""
Wrapper for 'mousepad' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_mousepad(self):
        """
        Return mousepad Command class object.
        """
        return self._mousepad

    def parse(self, args):
        """
        Parse arguments
        """
        self._mousepad = syslib.Command('mousepad')
        self._mousepad.set_args(args[1:])
        self._filter = '^$|recently-used.xbel'


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

        try:
            options.get_mousepad().run(filter=options.get_filter(), mode='background')
        except syslib.SyslibError as exception:
            raise SystemExit(exception)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
