#!/usr/bin/env python3
"""
Run CLAMAV anti-virus scanner.
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

        self._clamscan = syslib.Command("clamscan")
        self._clamscan.setFlags([ "-r" ])
        self._clamscan.setArgs(self._args.files)


    def getClamscan(self):
        """
        Return clamscan Command class object.
        """
        return self._clamscan


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Run ClamAV anti-virus scanner.")

        parser.add_argument("files", nargs="+", metavar="file", help="File or directory.")

        self._args = parser.parse_args(args)


class Clam(syslib.Dump):


    def __init__(self, options):
        self._clamscan = options.getClamscan()


    def run(self):
        self._clamscan.run()
        print("---------- VIRUS DATABASE ----------")
        if os.name == "nt":
            os.chdir(os.path.join(os.path.dirname(self._clamscan.getFile())))
            directory = "database"
        elif os.path.isdir("/var/clamav"):
            directory = "/var/clamav"
        else:
            directory = "/var/lib/clamav"
        for file in sorted(glob.glob(os.path.join(directory, "*c[lv]d"))):
            fileStat = syslib.FileStat(file)
            print("{0:10d} [{1:s}] {2:s}".format(fileStat.getSize(), fileStat.getTimeLocal(), file))
        return self._clamscan.getExitcode()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            sys.exit(Clam(options).run())
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
