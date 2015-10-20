#!/usr/bin/env python3
"""
LibreOffice launcher
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
        self._soffice = syslib.Command(os.path.join("program", "soffice"))
        self._soffice.setArgs(args[1:])
        if args[1:] == ["--version"]:
            self._soffice.run(mode="exec")
        self._filter = ("^$|: GLib-CRITICAL |: GLib-GObject-WARNING |: Gtk-WARNING |"
                        ": wrong ELF class:|: Could not find a Java Runtime|"
                        ": failed to read path from javaldx|^Failed to load module:|"
                        "unary operator expected|: unable to get gail version number|gtk printer")
        self._config()
        self._setenv()

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getSoffice(self):
        """
        Return soffice Command class object.
        """
        return self._soffice

    def _config(self):
        for file in glob.glob(".~lock.*#"):  # Remove stupid lock files
            try:
                os.remove(file)
            except OSError:
                pass

    def _setenv(self):
        if "GTK_MODULES" in os.environ:
            del os.environ["GTK_MODULES"]  # Fix Linux "gnomebreakpad" problems


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getSoffice().run(filter=options.getFilter(), mode="background")
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
            files = glob.glob(arg)  # Fixes Windows globbing bug
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
