#!/usr/bin/env python3
"""
Run daemon to update time once every 24 hours
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._ntpdate = syslib.Command("ntpdate", pathextra=[ "/usr/sbin" ])
        self._ntpdate.setArgs([ "pool.ntp.org" ])

        if len(args) == 1 or args[1] != "-u":
            self._ntpdate.run(mode="exec")


    def getNtpdate(self):
        """
        Return ntpdate Command class object.
        """
        return self._ntpdate


class Update(syslib.Dump):


    def __init__(self, options):
        while True:
            options.getNtpdate().run(mode="batch")
            if not options.getNtpdate().hasError():
                print("NTP Time updated =", time.strftime("%Y-%m-%d-%H:%M:%S"))
                time.sleep(86340)
            time.sleep(60)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Update(options)
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
