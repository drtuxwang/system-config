#!/usr/bin/env python3
"""
Play AVI/FLV/MP4 files in directory.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import random
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


    def getShuffleFlag(self):
        """
        Return shuffle flag.
        """
        return self._args.shuffleFlag


    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Play AVI/FLV/MP4 video files in directory.")

        parser.add_argument("-s", dest="shuffleFlag", action="store_true",
                            help="Shuffle order of the media files.")
        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="View information.")
        parser.add_argument("directories", nargs="+", metavar="directory",
                            help="Video directory.")

        self._args = parser.parse_args(args)


class Play(syslib.Dump):


    def __init__(self, options):
        self._play = syslib.Command("play")

        if options.getViewFlag():
            self._play.setFlags([ "-v" ])
        for directory in options.getDirectories():
            if not os.path.isdir(directory):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" media directory.')
            files = self._getfiles(directory, "*.avi", "*.flv", "*.mp4")
            if options.getShuffleFlag():
                random.shuffle(files)
            self._play.extendArgs(files)


    def run(self):
        self._play.run()
        if self._play.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._play.getExitcode()) +
                             ' received from "' + self._play.getFile() + '".')


    def _getfiles(self, directory, *patterns):
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
        return sorted(files)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Play(options).run()
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
