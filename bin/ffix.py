#!/usr/bin/env python3
"""
Remove horrible characters in filenames.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import re
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        if len(args) == 1 or args[1] in ("-h", "--h", "--help"):
            self._parseArgs(args[1:])

        self._files = args[1:]

    def getFiles(self):
        """
        Return list to files.
        """
        return self._files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Remove horrible charcters in filename.")

        parser.add_argument("files", nargs="+", metavar="file", help="File or directory.")

        self._args = parser.parse_args(args)


class Ffix(syslib.Dump):

    def __init__(self, options):
        isbadChar = re.compile("^-|[ !\"$&`'()*<>?\[\]|]")
        for file in options.getFiles():
            newfile = isbadChar.sub("_", file)
            if newfile != file:
                if not os.path.isfile(newfile):
                    if not os.path.isdir(newfile):
                        if not os.path.islink(newfile):
                            try:
                                os.rename(file, newfile)
                            except OSError:
                                pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Ffix(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
