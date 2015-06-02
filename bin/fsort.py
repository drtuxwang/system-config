#!/usr/bin/env python3
"""
Unicode sort lines of a file.
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


    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Unicode sort lines of a file.")

        parser.add_argument("files", nargs=1, metavar="file",
                            help="File contents to sort.")

        self._args = parser.parse_args(args)


class Sort(syslib.Dump):


    def __init__(self, options):
        self._lines = []
        if len(options.getFiles()):
            for file in options.getFiles():
                try:
                    with open(file, errors="replace") as ifile:
                        for line in ifile:
                            line = line.rstrip("\r\n")
                            self._lines.append(line)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
        else:
            for line in sys.stdin:
                self._lines.append(line.rstrip("\r\n"))
        self._lines = sorted(self._lines)


    def print(self):
        for line in self._lines:
            print(line)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Sort(options).print()
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
