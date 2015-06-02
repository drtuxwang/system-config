#!/usr/bin/env python3
"""
Wrapper for "eclipse" command (Ecilpse IDE for Java EE Developers)
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
        self._eclipse = syslib.Command("eclipse")
        if len(args) == 1:
            java = syslib.Command(os.path.join("bin", "java"))
            self._eclipse.setArgs([ "-vm", java.getFile(), "-vmargs", "-Xms2048m", "-Xmx2048m",
                                    "-XX:PermSize=8192m", "-XX:MaxPermSize=8192m",
                                    "-XX:-UseCompressedOops" ])
        else:
            self._eclipse.setArgs(args[1:])


    def getEclipse(self):
        """
        Return eclipse Command class object.
        """
        return self._eclipse


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getEclipse().run(mode="background")
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
