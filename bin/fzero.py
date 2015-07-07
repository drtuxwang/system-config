#!/usr/bin/env python3
"""
Zero device or create zero file.
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
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getLocation(self):
        """
        Return location.
        """
        return self._args.location[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Zero device or create zero file.")

        parser.add_argument("location", nargs=1, metavar="device|directory",
                            help='Device to zero or directory to create "fzero.tmp" file.')

        self._args = parser.parse_args(args)

        location = self._args.location[0]
        if os.path.exists(location):
            if os.path.isfile(location):
                raise SystemExit(sys.argv[0] + ': Cannot zero existing "' + location + '" file.')
        else:
            raise SystemExit(sys.argv[0] + ': Cannot find "' + location + '" device or directory.')


class Zerofile(syslib.Dump):


    def __init__(self, options):
        if os.path.isdir(options.getLocation()):
            file = os.path.join(options.getLocation(), "fzero.tmp")
            print('Creating "' + file + '" zero file...')
        else:
            file = options.getLocation()
            print('Zeroing "' + file + '" device...')
        startTime = time.time()
        chunk = 16384 * b"\0"
        size = 0
        try:
            with open(file, "wb") as ofile:
                while True:
                    for i in range(64):
                        ofile.write(chunk)
                    size += 1
                    sys.stdout.write("\r" + str(size) + " MB")
                    sys.stdout.flush()
        except (IOError, KeyboardInterrupt):
            pass
        elapsedTime = time.time() - startTime
        print(", {0:4.2f} seconds, {1:.0f} MB/s".format(elapsedTime, size / elapsedTime))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Zerofile(options)
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
