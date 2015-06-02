#!/usr/bin/env python3
"""
Search for packages that match regular expression in Debian package file.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
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


    def getPatterns(self):
        """
        Return list of regular expression search patterns.
        """
        return self._args.patterns


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Search for packages that match regular "
                                                     "expression in Debian package file.")

        parser.add_argument("packagesFile", nargs=1, metavar="distribution.package",
                            help="Debian package file.")
        parser.add_argument("patterns", nargs="+", metavar="pattern",
                            help="Regular expression.")

        self._args = parser.parse_args(args)


class Package(syslib.Dump):


    def __init__(self, version, size, description):
        self._version = version
        self._size = size
        self._description = description


    def getDescription(self):
        """
        Return description.
        """
        return self._description


    def setDescription(self, description):
        """
        Set package description.
        """
        self._description = description


    def getSize(self):
        """
        Return size.
        """
        return self._size


    def setSize(self, size):
        """
        Set package size.
        """
        self._size = size


    def getVersion(self):
        """
        Return version.
        """
        return self._version


    def setVersion(self, version):
        """
        Set package version.

        version = package version.
        """
        self._version = version


class Search(syslib.Dump):


    def __init__(self, options):
        self._readDistributionPackages(options.getPackagesFile())
        self._searchDistributionPackages(options.getPatterns())


    def _readDistributionPackages(self, packagesFile):
        self._packages = {}
        name = ""
        package = Package("", -1, "")
        try:
            with open(packagesFile, errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip("\r\n")
                    if line.startswith("Package: "):
                        name = line.replace("Package: ", "")
                    elif line.startswith("Version: "):
                        package.setVersion(line.replace("Version: ", "", 1).split(":")[-1])
                    elif line.startswith("Installed-Size: "):
                        try:
                            package.setSize(int(line.replace("Installed-Size: ", "", 1)))
                        except ValueError:
                            raise SystemExit(sys.argv[0] + ': Package "' + name +
                                             '" in "/var/lib/dpkg/info" has non integer size.')
                    elif line.startswith("Description: "):
                        package.setDescription(line.replace("Description: ", "", 1))
                        self._packages[name] = package
                        package = Package("", "0", "")
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + packagesFile + '" packages file.')


    def _searchDistributionPackages(self, patterns):
        for pattern in patterns:
            ispattern = re.compile(pattern, re.IGNORECASE)
            for name in sorted(self._packages.keys()):
                if (ispattern.search(name) or
                        ispattern.search(self._packages[name].getDescription())):
                    print("{0:25s} {1:15s} {2:5d}KB {3:s}".format(name.split(":")[0],
                          self._packages[name].getVersion(), self._packages[name].getSize(),
                          self._packages[name].getDescription()))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Search(options)
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
