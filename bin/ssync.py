#!/usr/bin/env python3
"""
Securely synchronize file system using SSH protocol.
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

        ssh = syslib.Command("ssh")

        self._rsync = syslib.Command("rsync")
        self._rsync.setFlags([ "-l", "-p", "-r", "-t", "-v", "-z", "-e",
                               ssh.getFile(), "--delete" ])
        self._rsync.setArgs([ self._args.source[0], self._args.target[0] ])


    def getRsync(self):
        """
        Return rsync Command class object.
        """
        return self._rsync


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Securely synchronize file system using SSH protocol.")

        parser.add_argument("source", nargs=1, metavar="[[user1@]host1:]source",
                            help="Source location.")
        parser.add_argument("target", nargs=1, metavar="[[user1@]host1:]target",
                            help="Target location.")

        self._args = parser.parse_args(args)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getRsync().run(filter="^$")
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getRsync().getExitcode())


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
