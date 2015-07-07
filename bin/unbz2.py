#!/usr/bin/env python3
"""
Uncompress a file in BZIP2 format.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
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

        self._bzip2 = syslib.Command("bzip2")

        if self._args.testFlag:
            self._bzip2.setFlags([ "-t" ])
        else:
            self._bzip2.setFlags([ "-d" ])
        self._bzip2.setArgs(self._args.archives)


    def getBzip2(self):
        """
        Return bzip2 Command class object.
        """
        return self._bzip2


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Uncompress a file in BZIP2 format.")

        parser.add_argument("-test", dest="testFlag", action="store_true",
                            help="Test archive data only.")

        parser.add_argument("archives", nargs="+", metavar="file.bz2", help="Archive file.")

        self._args = parser.parse_args(args)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getBzip2().run(mode="exec")
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
