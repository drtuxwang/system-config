#!/usr/bin/env python3
"""
Wrapper for "mousepad" command
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_mousepad(self):
        """
        Return mousepad Command class object.
        """
        return self._mousepad

    def parse(self, args):
        """
        Parse arguments
        """
        self._mousepad = command_mod.Command('mousepad', errors='stop')
        self._mousepad.set_args(args[1:])
        self._pattern = (
            '^$|recently-used.xbel|: Error retrieving accessibility bus|'
            ': GLib-CRITICAL |: GtkSourceView-CRITICAL|: Gtk-WARNING |'
            ': WARNING '
        )


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
        options = Options()

        subtask_mod.Background(options.get_mousepad().get_cmdline()).run(
            pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
