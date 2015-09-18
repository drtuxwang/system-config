#!/usr/bin/env python3
"""
Count number of lines and maximum columns used in file.
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
            description="Count number of lines and maximum columns used in file.")

        parser.add_argument("files", nargs="+", metavar="file", help="File to examine.")

        self._args = parser.parse_args(args)


class Count(syslib.Dump):

    def __init__(self, options):
        for file in options.getFiles():
            if os.path.isfile(file):
                if not os.path.isfile(file):
                    raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
                nlines = 0
                maxline = 0
                maxcols = 0
                try:
                    with open(file, errors="replace") as ifile:
                        for line in ifile:
                            nlines += 1
                            ncols = len(line.rstrip("\r\n"))
                            if ncols > maxcols:
                                maxcols = ncols
                                lline = nlines
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
                except UnicodeDecodeError:  # Non text file
                    continue
                print("{0:s}: {1:d} lines (max length of {2:d} on line {3:d})".format(
                      file, nlines, maxcols, lline))


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Count(options)
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
