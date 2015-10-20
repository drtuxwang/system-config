#!/usr/bin/env python3
"""
Automatic connection to FTP server anonymously.
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

        self._ftp = syslib.Command("ftp")
        self._ftp.setArgs(["-i", self._args.host[0]])

        self._netrc(self._args.host[0])

    def getFtp(self):
        """
        Return ftp Command class object.
        """
        return self._ftp

    def _netrc(self, host):
        if "HOME" in os.environ:
            netrc = os.path.join(os.environ["HOME"], ".netrc")
            umask = os.umask(int("077", 8))
            try:
                with open(netrc, "w", newline="\n") as ofile:
                    print("machine", host,
                          "login anonymous password someone@somehost.somecompany.com", file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + netrc +
                                 '" configuration file.')
            os.umask(umask)

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Automatic connection to FTP server anonymously.")

        parser.add_argument("host", nargs=1, help="Ftp host.")

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        if os.name == "nt":
            self._windowsArgv()
        self._signals()
        try:
            options = Options(sys.argv)
            options.getFtp().run(mode="exec")
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
