#!/usr/bin/env python3
"""
Reset to default screen resolution
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import os
import signal
import time

import syslib


class Xreset(syslib.Dump):


    def __init__(self):
        self._xrandr = syslib.Command("xrandr")
        self._dpi = "96"


    def run(self):
        self._xrandr.setArgs([ "-s", "0" ])
        self._xrandr.run(mode="batch")
        time.sleep(1)
        self._xrandr.setArgs([ "--dpi", self._dpi ])
        self._xrandr.run(mode="batch")


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            Xreset().run()
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
