#!/usr/bin/env python3
"""
Checks whether a host is up.
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

        if os.path.isfile("/usr/sbin/ping"):
            self._ping = syslib.Command(file="/usr/sbin/ping")
        elif os.path.isfile("/usr/etc/ping"):
            self._ping = syslib.Command(file="/usr/etc/ping")
        else:
            self._ping = syslib.Command("ping")

        host = self._args.host[0]
        self._filter = "min/avg/max"
        if syslib.info.getSystem() == "linux":
            self._ping.setArgs(["-h"])
            self._ping.run(filter="[-]w ", mode="batch")
            if self._ping.hasOutput():
                self._ping.setArgs(["-w", "4", "-c", "3", host])
            else:
                self._ping.setArgs(["-c", "3", host])
        elif syslib.info.getSystem() == "sunos":
            self._ping.setArgs(["-s", host, "64", "3"])
        elif os.name == "nt":
            self._ping.setArgs(["-w", "4", "-n", "3", host])
            self._filter = "Minimum|TTL"
        else:
            self._ping.setArgs(["-w", "4", "-c", "3", host])

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getHost(self):
        """
        Return host.
        """
        return self._args.host[0]

    def getPing(self):
        """
        Return ping Command class object.
        """
        return self._ping

    def getRepeatFlag(self):
        """
        Return repeat flag.
        """
        return self._args.repeatFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Checks whether a host is up.")

        parser.add_argument("-f", dest="repeatFlag", action="store_true",
                            help="Monitor host every five seconds.")

        parser.add_argument("host", nargs=1, help="Host to monitor.")

        self._args = parser.parse_args(args)


class Isitup(syslib.Dump):

    def __init__(self, options):
        stat = ""
        while options.getRepeatFlag():
            test = self._ping(options)
            if test != stat:
                print(time.strftime("%Y-%m-%d-%H:%M:%S") + ": " + test)
                stat = test
            time.sleep(5)
        print(self._ping(options))

    def _ping(self, options):
        options.getPing().run(filter=options.getFilter(), mode="batch")
        if options.getPing().hasOutput():
            return options.getHost() + " is alive"
        else:
            return options.getHost() + " is dead"


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Isitup(options)
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
