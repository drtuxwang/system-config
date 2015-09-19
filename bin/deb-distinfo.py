#!/usr/bin/env python3
"""
Show information about packages in Debian packages list file.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getPackagesFile(self):
        """
        Return packages file location.
        """
        return self._args.packagesFile[0]

    def getPackageNames(self):
        """
        Return list of package names.
        """
        return self._args.packageNames

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Show information about packages in Debian packages list file.")

        parser.add_argument("packagesFile", nargs=1, metavar="distribution.package",
                            help="Debian package list file.")
        parser.add_argument("packageNames", nargs="+", metavar="package", help="Package name.")

        self._args = parser.parse_args(args)


class Info(syslib.Dump):

    def __init__(self, options):
        self._readDistributionPackages(options.getPackagesFile())
        self._showDistributionPackages(options.getPackageNames())

    def _readDistributionPackages(self, packagesFile):
        self._packages = {}
        name = ""
        lines = []
        try:
            with open(packagesFile, errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip("\r\n")
                    if line.startswith("Package: "):
                        name = line.replace("Package: ", "")
                        lines = [line]
                    elif line:
                        lines.append(line)
                    else:
                        self._packages[name] = lines
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + packagesFile + '" packages file.')

    def _showDistributionPackages(self, packageNames):
        for name in packageNames:
            if name in self._packages.keys():
                for line in self._packages[name]:
                    print(line)
                print()


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Info(options)
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
