#!/usr/bin/env python3
"""
Make a compressed archive in TAR.XZ format.
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

        self._tar = syslib.Command("tar")
        self._tar.setFlags([ "cfvJ", self._archive ] + self._files)

        os.environ["XZ_OPT"] = "-9 -e"


    def getTar(self):
        """
        Return tar Command class object.
        """
        return self._tar


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Make a compressed archive in TAR.XZ format.")

        parser.add_argument("archive", nargs=1, metavar="file.tar.xz|file.txz",
                            help="Archive file.")
        parser.add_argument("files", nargs="*", metavar="file",
                            help="File or directory.")

        self._args = parser.parse_args(args)

        if os.path.isdir(self._args.archive[0]):
             self._archive = os.path.abspath(self._args.archive[0]) + ".tar.xz"
        else:
             self._archive = self._args.archive[0]
        if not self._archive.endswith(".tar.xz") and not self._archive.endswith(".txz"):
            raise SystemExit(sys.argv[0] + ': Unsupported "' + self._archive + '" archive format.')

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getTar().run(mode="exec")
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
