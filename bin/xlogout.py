#!/usr/bin/env python3
"""
Shutdown X-windows
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import os
import shutil
import signal

import syslib


class Logout(syslib.Dump):


    def __init__(self):
        self._pid = 0
        if "SESSION_MANAGER" in os.environ.keys():
            try:
                self._pid = int(os.path.basename(os.environ["SESSION_MANAGER"]))
            except ValueError:
                pass


    def run(self):
        try:
            answer = input("Do you really want to logout of X-session? (y/n) [n] ")
            if answer.lower() != "y":
                raise SystemExit(1)
        except EOFError:
            pass
        except KeyboardInterrupt:
            sys.exit(114)
        syslib.Task().killpids([ self._pid ])


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            Logout().run()
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
