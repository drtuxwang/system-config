#!/usr/bin/env python3
"""
Wrapper for "thunderbird" command
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
        self._thunderbird = syslib.Command("thunderbird")
        if len(args) > 1:
            self._thunderbird.setArgs(args[1:])
            if args[1] in ("-v", "-version", "--version"):
                self._thunderbird.run(mode="exec")

        self._filter = "^added$|profile-after-change|mail-startup-done"

        self._config()

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getThunderbird(self):
        """
        Return thunderbird Command class object.
        """
        return self._thunderbird

    def _config(self):
        if "HOME" in os.environ:
            thunderbirddir = os.path.join(os.environ["HOME"], ".thunderbird")
            if os.path.isdir(thunderbirddir):
                os.chmod(thunderbirddir, int("700", 8))


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getThunderbird().run(filter=options.getFilter(), mode="background")
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
