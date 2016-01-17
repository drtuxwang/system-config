#!/usr/bin/env python3
"""
PUNK BUSTER SETUP launcher
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
        self._pbsetup = syslib.Command('pbsetup.run', check=False)
        if not self._pbsetup.is_found():
            self._pbsetup = syslib.Command('pbsetup')
        self._pbsetup.set_args(args[1:])
        self._filter = ': wrong ELF class:|: Gtk-WARNING '

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_pbsetup(self):
        """
        Return pbsetup Command class object.
        """
        return self._pbsetup


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
            options.get_pbsetup().run(filter=options.get_filter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.get_pbsetup().get_exitcode())

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
