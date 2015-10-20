#!/usr/bin/env python3
"""
Wrapper for "skype" command
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
        self._skype = syslib.Command("skype")
        self._skype.setArgs(args[1:])
        self._filter = "^Fontconfig "
        self._setLibraries(self._skype)

        # Prevent creation of "fontconfig" directory
        if "HOME" in os.environ:
            os.chdir(os.path.dirname(os.environ["HOME"]))

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getSkype(self):
        """
        Return skype Command class object.
        """
        return self._skype

    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), "lib")
        if os.path.isdir(libdir):
            if syslib.info.getSystem() == "linux":
                if "LD_LIBRARY_PATH" in os.environ:
                    os.environ["LD_LIBRARY_PATH"] = (
                        libdir + os.pathsep + os.environ["LD_LIBRARY_PATH"])
                else:
                    os.environ["LD_LIBRARY_PATH"] = libdir


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getSkype().run(filter=options.getFilter(), mode="background")
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
