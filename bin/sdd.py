#!/usr/bin/env python3
"""
Securely backup/restore partitions using SSH protocol.
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

        source = self._args.source[0]
        target = self._args.target[0]
        if ":" in source:
            if ":" in target:
                raise SystemExit(
                    sys.argv[0] + ": Source or target cannot both be remote device/file.")
            host, file = source.split(":")[:2]
            device = target
            print('Restoring "' + device + '" from', host + ':' + file + '...')
            self._command1 = syslib.Command("ssh", args=[host, "cat " + file])
            self._command2 = syslib.Command("dd", args=["of=" + device])
        else:
            if ":" not in target:
                raise SystemExit(
                    sys.argv[0] + ": Source or target cannot both be local device/file.")
            elif not os.path.exists(source):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + source + '" device or file.')
            device = source
            host, file = target.split(":")[:2]
            print('Backing up "' + device + '" to', host + ':' + file + '...')
            self._command1 = syslib.Command("dd", args=["if=" + device])
            self._command2 = syslib.Command("ssh", args=[host, "cat - > " + file])

    def getCommand1(self):
        """
        Return command1 Command class object.
        """
        return self._command1

    def getCommand2(self):
        """
        Return command2 Command class object.
        """
        return self._command2

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Securely backup/restore partitions using SSH protocol.")

        parser.add_argument("source", nargs=1, metavar="[[user1@]host1:]source",
                            help="Source device/file location.")
        parser.add_argument("target", nargs=1, metavar="[[user1@]host1:]target",
                            help="Target device/file location.")

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getCommand1().run(pipes=[options.getCommand2()])
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getCommand1().getExitcode())

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
