#!/usr/bin/env python3
"""
Fix JSON indention.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import json
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
        parser = argparse.ArgumentParser(description="Fix JSON indenting.")

        parser.add_argument("files", nargs="+", metavar="file", help="JSON file.")

        self._args = parser.parse_args(args)


class Indent(syslib.Dump):

    def __init__(self, options):
        for file in options.getFiles():
            try:
                with open(file) as ifile:
                    data = json.load(ifile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" JSON file.')
            except (KeyError, ValueError):
                raise SystemExit(sys.argv[0] + ': Format error in "' + file + '" JSON file.')
            print(json.dumps(data, indent=4, sort_keys=True))


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Indent(options)
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
