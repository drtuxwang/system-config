#!/usr/bin/env python3
"""
Locate a program file.
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
            self._extensions = os.environ["PATHEXT"].lower().split(os.pathsep) + [ ".py", "" ]
        else:
            self._extensions = [ "" ]


    def getAllFlag(self):
        """
        Return all flag.
        """
        return self._args.allFlag


    def getExtensions(self):
        """
        Return list of executable extensions.
        """
        return self._extensions


    def getPrograms(self):
        """
        Return list of programs.
        """
        return self._args.programs


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Locate a program file.")

        parser.add_argument("-a", dest="allFlag", action="store_true",
                            help="Show the location of all occurances.")

        parser.add_argument("programs", nargs="+", metavar="program", help="Command to search.")

        self._args = parser.parse_args(args)


class Which(syslib.Dump):


    def __init__(self, options):
        self._options = options
        self._path = os.environ["PATH"]
        for program in options.getPrograms():
            self._locate(program)


    def _locate(self, program):
        found = []
        for directory in self._path.split(os.pathsep):
            if os.path.isdir(directory):
                for extension in self._options.getExtensions():
                    file = os.path.join(directory, program) + extension
                    if file not in found:
                        if os.path.isfile(file):
                            found.append(file)
                            print(file)
                            if not self._options.getAllFlag():
                                return

        if not found:
            print(program, "not in:")
            for directory in self._path.split(os.pathsep):
                print(" ", directory)
        raise SystemExit(1)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Which(options)
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
