#!/usr/bin/env python3
"""
Check whether installed debian packages in ".debs" list have updated versions.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import copy
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getListFiles(self):
        """
        Return list of installed packages files.
        """
        return self._args.listFiles

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Check whether installed debian packages in '
                                                     '".debs" list have updated versions.')

        parser.add_argument("listFiles", nargs="+", metavar="distribution.debs",
                            help="Debian installed packages list file.")

        self._args = parser.parse_args(args)


class Package(syslib.Dump):

    def __init__(self, version="0", depends=[], url=""):
        self._version = version
        self._depends = depends
        self._url = url

    def getDepends(self):
        """
        Return list of required dependent packages.
        """
        return self._depends

    def setDepends(self, depends):
        """
        Set list of required dependent packages.

        depends = List of required dependent packages
        """
        self._depends = depends

    def getUrl(self):
        """
        Return package url.
        """
        return self._url

    def setUrl(self, url):
        """
        Set package url.

        url = Package url
        """
        self._url = url

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


class CheckUpdates(syslib.Dump):

    def __init__(self, options):
        ispattern = re.compile("[.]debs-?.*$")
        for listFile in options.getListFiles():
            if syslib.FileStat(listFile).getSize() > 0:
                if os.path.isfile(listFile):
                    if ispattern.search(listFile):
                        distribution = ispattern.sub("", listFile)
                        print('\nChecking "' + listFile + '" list file...')
                        self._packages = self._readDistributionPackages(distribution + ".packages")
                        self._readDistributionPinPackages(distribution + ".pinlist")
                        self._readDistributionBlacklist(distribution + ".blacklist")
                        self._checkDistributionUpdates(distribution, listFile)

    def _readDistributionPackages(self, packagesFile):
        packages = {}
        name = ""
        package = Package()
        try:
            with open(packagesFile, errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip("\r\n")
                    if line.startswith("Package: "):
                        name = line.replace("Package: ", "")
                    elif line.startswith("Version: "):
                        package.setVersion(line.replace("Version: ", "").split(":")[-1])
                    elif line.startswith("Depends: "):
                        depends = []
                        for i in line.replace("Depends: ", "").split(", "):
                            depends.append(i.split()[0])
                        package.setDepends(depends)
                    elif line.startswith("Filename: "):
                        package.setUrl(line[10:])
                        packages[name] = package
                        package = Package()
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + packagesFile + '" packages file.')
        return packages

    def _readDistributionPinPackages(self, pinFile):
        packagesCache = {}
        try:
            with open(pinFile, errors="replace") as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        pattern = columns[0]
                        if pattern[:1] != "#":
                            file = os.path.join(os.path.dirname(pinFile), columns[1]) + ".packages"
                            if file not in packagesCache.keys():
                                packagesCache[file] = self._readDistributionPackages(file)
                            ispattern = re.compile(pattern+"$")
                            for key, value in packagesCache[file].items():
                                if ispattern.match(key):
                                    self._packages[key] = copy.copy(packagesCache[file][key])
        except IOError:
            pass

    def _readDistributionBlacklist(self, file):
        try:
            with open(file, errors="replace") as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        name = columns[0]
                        if name[:1] != "#":
                            if name in self._packages.keys():
                                if (columns[1] == "*" or
                                        columns[1] == self._packages[name].getVersion()):
                                    del self._packages[name]
        except IOError:
            return

    def _checkDistributionUpdates(self, distribution, listFile):
        try:
            with open(listFile, errors="replace") as ifile:
                versions = {}
                for line in ifile:
                    if line[:1] != "#":
                        try:
                            name, version = line.split()[:2]
                        except ValueError:
                            raise SystemExit(sys.argv[0] + ': Format error in "' +
                                             os.path.join(distribution, "packages.ilist") + '".')
                        versions[name] = version
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + listFile + '" file.')

        urlfile = os.path.basename(distribution) + listFile.split(".debs")[-1]+".url"
        try:
            with open(urlfile, "w", newline="\n") as ofile:
                for name in sorted(versions.keys()):
                    if name in self._packages.keys():
                        if self._packages[name].getVersion() != versions[name]:
                            file = self._local(distribution, self._packages[name].getUrl())
                            print(file, "(Replaces", versions[name] + ")")
                            print(file, file=ofile)
                            for name in sorted(self._depends(versions,
                                                             self._packages[name].getDepends())):
                                if name in self._packages.keys():
                                    file = self._local(distribution, self._packages[name].getUrl())
                                    print("  " + file, "(New dependency)")
                                    print("  " + file, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _depends(self, versions, depends):
        names = []
        for name in depends:
            if name not in versions.keys():
                versions[name] = ""
                names.append(name)
                if name in self._packages.keys():
                    names.extend(self._depends(versions, self._packages[name].getDepends()))
        return names

    def _local(self, distribution, url):
        file = os.path.join(distribution, os.path.basename(url))
        if os.path.isfile(file):
            return "file://" + os.path.abspath(file)
        return url


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            CheckUpdates(options)
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
