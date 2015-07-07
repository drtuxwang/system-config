#!/usr/bin/env python3
"""
Speak words using Espeak TTS engine.
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

        self._espeak = syslib.Command("espeak")
        self._espeak.setFlags([ "-a128", "-k30", "-ven+f2", "-s60", "-x" ])
        if self._args.voice:
            self._espeak.appendFlag("-v" + self._args.voice[0])
        self._espeak.setArgs([ " ".join(self._args.words) ])

        self._filter = "^ALSA lib|: Connection refused|^Cannot connect|^jack server"


    def getEspeak(self):
        """
        Return espeak Command class object.
        """
        return self._espeak


    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Speak words using Espeak TTS engine.")

        parser.add_argument("-voice", nargs=1, metavar="xx+yy",
                            help="Select language voice (ie en+f2, fr+m3, de+f2, zhy+f2).")

        parser.add_argument("words", nargs="+", metavar="word",
                            help="A word.")

        self._args = parser.parse_args(args)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getEspeak().run(filter=options.getFilter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getEspeak().getExitcode())


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
