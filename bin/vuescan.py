#!/usr/bin/env python3
"""
Wrapper for "vuescan" command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._vuescan = syslib.Command("vuescan")
        self._vuescan.setArgs(args[1:])
        self._filter = "^$|: LIBDBUSMENU-|: Gtk-WARNING"


    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter


    def getVuescan(self):
        """
        Return vuescan Command class object.
        """
        return self._vuescan


class Main:


    def __init__(self):
        self._signals()
        try:
            options = Options(sys.argv)
            options.getVuescan().run(filter=options.getFilter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
