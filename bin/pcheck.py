#!/usr/bin/env python3
"""
Check JPEG picture files.
"""

import argparse
import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getDirectories(self):
        """
        Return list of directories.
        """
        return self._args.directories


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Check JPEG picture files.")

        parser.add_argument("directories", nargs="+", metavar="directory",
                            help="Directory containing JPEG files to check.")

        self._args = parser.parse_args(args)


class Check(syslib.Dump):


    def __init__(self, options):
        self._directories = options.getDirectories()


    def run(self):
        errors = []
        jpeginfo = syslib.Command("jpeginfo", flags=[ "--info", "--check" ])
        for directory in self._directories:
            if os.path.isdir(directory):
                files = []
                for file in glob.glob(os.path.join(directory, "*.*")):
                    if file.split(".")[-1].lower() in ( "jpg", "jpeg" ):
                        files.append(file)
                if files:
                    jpeginfo.setArgs(files)
                    jpeginfo.run(mode="batch")
                    for line in jpeginfo.getOutput():
                        if "[ERROR]" in line:
                            errors.append(line)
                        else:
                            print(line)
        if errors:
            for line in errors:
                print(line)
            raise SystemExit("Total errors encountered: " + str(len(errors)) + ".")


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Check(options).run()
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
