#!/usr/bin/env python3
"""
Play system bell sound
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        sound = args[0][:-3] + ".ogg"  # Replace ".py" with ".ogg"
        if not os.path.isfile(sound):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + sound + '" file.')
        self._bell = syslib.Command("ogg123", check=False)
        if not self._bell.isFound():
            self._bell = syslib.Command("cvlc", flags=["--play-and-exit"], check=False)
            if not self._bell.isFound():
                raise SystemExit(sys.argv[0] + ': Cannot find required "ogg123" or'
                                 ' "cvlc" software.')
        self._bell.setArgs([sound])

    def getBell(self):
        """
        Return bell Command class object.
        """
        return self._bell


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getBell().run(mode="batch")
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getBell().getExitcode())

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
