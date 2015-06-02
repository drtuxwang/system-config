#!/usr/bin/env python3
"""
Concatenate files and print on the standard output.
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
        parser = argparse.ArgumentParser(
                description="Concatenate files and print on the standard output.")

        parser.add_argument("files", nargs="+", metavar="file", help="File to view.")

        self._args = parser.parse_args(args)


class Cat(syslib.Dump):


    def __init__(self, options):
        if len(options.getFiles()) == 0:
            self._pipe(sys.stdin.buffer)
        else:
            for file in options.getFiles():
                self._file(file)


    def _file(self, file):
        try:
            with open(file, "rb") as ifile:
                self._pipe(ifile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')


    def _pipe(self, pipe):
        while True:
            data = pipe.read(4096)
            if len(data) == 0:
                break
            sys.stdout.buffer.write(data)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Cat(options)
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
