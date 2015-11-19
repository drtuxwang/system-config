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


class Options:

    def __init__(self, args):
        self._pbsetup = syslib.Command('pbsetup.run', check=False)
        if not self._pbsetup.isFound():
            self._pbsetup = syslib.Command('pbsetup')
        self._pbsetup.setArgs(args[1:])
        self._filter = ': wrong ELF class:|: Gtk-WARNING '

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getPbsetup(self):
        """
        Return pbsetup Command class object.
        """
        return self._pbsetup


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getPbsetup().run(filter=options.getFilter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getPbsetup().getExitcode())

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
