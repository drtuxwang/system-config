#!/usr/bin/env python3
"""
Run DSMJ backup system
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
        self._dsmj = syslib.Command("dsmj")
        self._dsmj.setArgs(args[1:])
        self._config()

    def getDsmj(self):
        """
        Return dsmj Command class object.
        """
        return self._dsmj

    def _config(self):
        if "HOME" in os.environ:
            directory = os.path.join(os.environ["HOME"], ".dsmj")
            try:
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                os.chdir(directory)
            except OSError:
                pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getDsmj().run(mode="background")
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
