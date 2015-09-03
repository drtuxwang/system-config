#!/usr/bin/env python3
"""
Youtube video downloader.
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

        self._youtubedl = syslib.Command("youtube-dl", check=False)
        if not self._youtubedl.isFound():
            youtube = syslib.Command("youtube", args=args[1:], check=False)
            if youtube.isFound():
                youtube.run(mode="exec")
            self._youtubedl = syslib.Command("youtube-dl")

        if self._args.viewFlag:
            self._youtubedl.setArgs([ "--list-formats" ])
        elif self._args.format:
            self._youtubedl.setArgs([ "--title", "--format", str(self._args.format[0]) ])
        self._youtubedl.extendArgs(self._args.urls)

        self._setpython(self._youtubedl)


    def getYoutubedl(self):
        """
        Return youtubedl Command class object.
        """
        return self._youtubedl


    def _setpython(self, command): # Must use system Python
        if os.path.isfile("/usr/bin/python3"):
            command.setWrapper(syslib.Command(file="/usr/bin/python3"))
        elif os.path.isfile("/usr/bin/python"):
            command.setWrapper(syslib.Command(file="/usr/bin/python"))


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Youtube video downloader.")

        parser.add_argument("-f", nargs=1, type=int, dest="format", metavar="code",
                            help="Select video format code.")
        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Show video format codes.")

        parser.add_argument("urls", nargs="+", metavar="url", help="Youtube video URL.")

        self._args = parser.parse_args(args)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getYoutubedl().run()
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
