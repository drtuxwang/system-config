#!/usr/bin/env python3
"""
Break reminder timer.
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
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        if self._args.guiFlag:
            xterm = syslib.Command("xterm")
            xterm.setArgs([ "-fn", "-misc-fixed-bold-r-normal--18-*-iso8859-1", "-fg", "#000000",
                            "-bg", "#ffffdd", "-cr", "#880000", "-geometry", "15x3", "-ut", "+sb",
                            "-e", sys.argv[0] ] + args[2:])
            xterm.run(mode="daemon")
            raise SystemExit(0)

        self._setpop()


    def getPop(self):
        """
        Return pop Command class object.
        """
        return self._pop


    def getTime(self):
        """
        Return time limit.
        """
        return self._args.time[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Break reminder timer.")

        parser.add_argument("-g", dest="guiFlag", action="store_true", help="Start GUI.")

        parser.add_argument("time", nargs=1, type=int, help="Time between breaks in minutes.")

        self._args = parser.parse_args(args)

        if self._args.time[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "break time.")


    def _setpop(self):
        self._pop = syslib.Command("notify-send")
        self._pop.setFlags([ "-t", "10000" ]) # 10 secodns display time


class StopWatch(syslib.Dump):


    def __init__(self, options):
        self._options = options
        self._bell = syslib.Command("bell")
        self._limit = options.getTime() * 60
        self._reset()


    def run(self):
        while True:
            try:
                sys.stdout.write("\033]11;#ffffdd\007")
                while True:
                    if self._elapsed >= self._limit + self._alarm:
                        self._alert()
                    time.sleep(1)
                    self._elapsed = int(time.time()) - self._start
                    sys.stdout.write(" \r " + time.strftime("%H:%M ") +
                                     str(self._limit-self._elapsed))
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print()
            self._reset()


    def _alert(self):
        if self._alarm < 601:
            sys.stdout.write("\033]11;#ff8888\007")
            sys.stdout.flush()
            self._bell.run(mode="batch")         # Avoids defunct process
            self._options.getPop().setArgs([ time.strftime("%H:%M") + ": break time reminder" ])
            # Avoids defunct process
            self._options.getPop().run(mode="batch")
        self._alarm += 60 # One minute reminder


    def _reset(self):
        self._alarm = 0
        self._elapsed = 0
        self._start = int(time.time())


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            StopWatch(options).run()
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
