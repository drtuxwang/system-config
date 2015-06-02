#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE graphical editor
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
        self._desktop = self._getDesktop()
        if self._desktop == "gnome":
            self._xedit = syslib.Command("gedit")
        elif self._desktop == "kde":
            self._xedit = syslib.Command("kate")
        elif self._desktop == "xfce":
            self._xedit = syslib.Command("mousepad")
        else:
            self._xedit = syslib.Command("vi")
        self._xedit.setArgs(args[1:])


    def getXedit(self):
        """
        Return xedit Command class object.
        """
        return self._xedit


    def _getDesktop(self):
        keys = os.environ.keys()
        if "XDG_MENU_PREFIX" in keys and os.environ["XDG_MENU_PREFIX"] == "xfce-":
            return "xfce"
        if "XDG_CURRENT_DESKTOP" in keys and os.environ["XDG_CURRENT_DESKTOP"] == "XFCE":
            return "xfce"
        if "XDG_DATA_DIRS" in keys and "/xfce" in os.environ["XDG_DATA_DIRS"]:
            return "xfce"
        if "DESKTOP_SESSION" in keys:
            if "gnome" in os.environ["DESKTOP_SESSION"]:
                return "gnome"
            if "kde" in os.environ["DESKTOP_SESSION"]:
                return "kde"
        if "GNOME_DESKTOP_SESSION_ID" in keys:
            return "gnome"
        return "Unknown"


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getXedit().run(mode="exec")
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
