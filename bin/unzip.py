#!/usr/bin/env python3
"""
Unpack a compressed archive in ZIP format.
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

        if os.name == "nt":
            self._archiver = syslib.Command("pkzip32.exe", check=False)
            if not self._archiver.isFound():
                self._archiver = syslib.Command("unzip")
        else:
            self._archiver = syslib.Command("unzip")

        if args[1] in ("view", "test"):
            self._archiver.setArgs(args[1:])
            self._archiver.run(mode="exec")

        if os.path.basename(self._archiver.getFile()) == "pkzip32.exe":
            if self._args.viewFlag:
                self._archiver.setFlags(["-view"])
            elif self._args.testFlag:
                self._archiver.setFlags(["-test"])
            else:
                self._archiver.setFlags(["-extract", "-directories"])
        else:
            if self._args.viewFlag:
                self._archiver.setFlags(["-v"])
            elif self._args.testFlag:
                self._archiver.setFlags(["-t"])

    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def getArchives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Unpack a compressed archive in ZIP format.")

        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Show contents of archive.")
        parser.add_argument("-test", dest="testFlag", action="store_true",
                            help="Test archive data only.")

        parser.add_argument("archives", nargs="+", metavar="file.zip",
                            help="Archive file.")

        self._args = parser.parse_args(args)


class Unpack(syslib.Dump):

    def __init__(self, options):
        os.umask(int("022", 8))
        archiver = options.getArchiver()
        for archive in options.getArchives():
            archiver.setArgs([archive])
            archiver.run()
            if archiver.getExitcode():
                print(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) +
                      ' received from "' + archiver.getFile() + '".', file=sys.stderr)
                raise SystemExit(archiver.getExitcode())


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unpack(options)
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
