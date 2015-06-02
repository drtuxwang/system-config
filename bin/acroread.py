#!/usr/bin/env python3
"""
Wrapper for "acroread" command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._acroread = syslib.Command(os.path.join("bin", "acroread"))
        self._acroread.setArgs(args[1:])
        self._filter = (
                "^$|Failed to load module:|wrong ELF class:| Gdk-WARNING | Gtk-CRITICAL |"
                " Gtk-WARNING |: Failed to load module|: too many arguments|"
                ": unexpected operator|dirname[: ]")
        self._setenv()


    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter


    def getAcroread(self):
        """
        Return acroread Command class object.
        """
        return self._acroread


    def _setenv(self):
        keys = os.environ.keys()
        if "GTK_MODULES" in keys: # Fix Linux "gnomebreakpad" problems
            del os.environ["GTK_MODULES"]
        if "LANG" in keys: # Fix Linux "gnomebreakpad" problems
            del os.environ["LANG"]
        if "LC_CTYPE" in keys: # Fix Linux "gnomebreakpad" problems
            del os.environ["LC_CTYPE"]


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getAcroread().run(filter=options.getFilter(), mode="background")
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
