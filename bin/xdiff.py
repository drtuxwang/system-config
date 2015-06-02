#!/usr/bin/env python3
"""
Graphical file comparison and merge tool.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self._meld = syslib.Command("meld")
        files = self._args.files
        if os.path.isdir(files[0]) and os.path.isfile(files[1]):
            self._meld.setArgs([ os.path.join(files[0], os.path.basename(files[1])), files[1] ])
        elif os.path.isfile(files[0]) and os.path.isdir(files[1]):
            self._meld.setArgs([ files[0], os.path.join(files[1], os.path.basename(files[0])) ])
        elif os.path.isfile(files[0]) and os.path.isfile(files[1]):
            self._meld.setArgs(args[1:])
        else:
            raise SystemExit(sys.argv[0] + ": Cannot compare two directories.")

        self._filter = "^$|: GtkWarning: |^  buttons =|^  gtk.main|recently-used.xbel"


    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter


    def getMeld(self):
        """
        Return meld Command class object.
        """
        return self._meld


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Graphical file comparison and merge tool.")

        parser.add_argument("files", nargs=2, metavar="file",
                            help="File to compare.")

        self._args = parser.parse_args(args)

        print("Usage: xdiff file1 file2")

class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getMeld().run(filter=options.getFilter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getMeld().getExitcode())


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
