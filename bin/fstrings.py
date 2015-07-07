#!/usr/bin/env python3
"""
Print the strings of printable characters in files.
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


    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Print the strings of printable characters in files.")

        parser.add_argument("files", nargs="+", metavar="file", help="File to search.")

        self._args = parser.parse_args(args)


class Strings(syslib.Dump):


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
        string = ""
        while True:
            data = pipe.read(4096)
            if len(data) == 0:
                break
            for byte in data:
                if byte > 31 and byte < 127:
                    string += chr(byte)
                else:
                    if len(string) >= 4:
                        print(string)
                    string = ""
        if string:
            print(string)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Strings(options)
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
