#!/usr/bin/env python3
"""
Make a compressed archive in DEB format or query database/files.
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

    def getArch(self):
        """
        Return sub architecture.
        """
        return self._arch

    def getArchSub(self):
        """
        Return sub architecture.
        """
        return self._archSub

    def getDpkg(self):
        """
        Return dpkg Command class object.
        """
        return self._dpkg

    def getMode(self):
        """
        Return operation mode.
        """
        return self._args.mode

    def getPackageNames(self):
        """
        Return list of package names.
        """
        return self._packageNames

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Make a compressed archive in DEB format or query database/files.")

        parser.add_argument("-l", action="store_const", const="list", dest="mode",
                            default="dpkg", help="Show all installed packages (optional arch).")
        parser.add_argument("-s", action="store_const", const="-s", dest="option",
                            help="Show status of selected installed packages.")
        parser.add_argument("-L", action="store_const", const="-L", dest="option",
                            help="Show files owned by selected installed packages.")
        parser.add_argument("-d", action="store_const", const="depends",
                            dest="mode", default="dpkg",
                            help="Show dependency tree for selected installed packages.")
        parser.add_argument("-P", action="store_const", const="-P", dest="option",
                            help="Remove selected installed packages.")
        parser.add_argument("-S", action="store_const", const="-S", dest="option",
                            help="Locate package which contain file.")
        parser.add_argument("-i", action="store_const", const="-i", dest="option",
                            help="Install selected Debian package files.")
        parser.add_argument("-I", action="store_const", const="-I", dest="option",
                            help="Show information about selected Debian package files.")

        parser.add_argument("args", nargs="*", metavar="package.deb|package|arch",
                            help="Debian package file, package name or arch.")

        self._args = parser.parse_args(args)

        self._dpkg = syslib.Command("dpkg")
        self._dpkg.setArgs(["--print-architecture"])
        self._dpkg.run(mode="batch")
        if len(self._dpkg.getOutput()) != 1:
            raise SystemExit(sys.argv[0] + ': Cannot detect default architecture of packages.')
        self._arch = self._dpkg.getOutput()[0]

        if self._args.mode == "list":
            if self._args.args:
                self._archSub = self._args.args[0]
            else:
                self._archSub = ""
        elif self._args.mode == "depends":
            self._packageNames = self._args.args
        elif self._args.option:
            self._dpkg.setArgs([self._args.option] + self._args.args)
        elif len(self._args.args) and self._args.args[0].endswith(".deb"):
            self._dpkg = syslib.Command("dpkg-deb")
            self._dpkg.setArgs(["-b", os.curdir, self._args.args[0]])
        elif self._args.args:
            raise SystemExit(sys.argv[0] + ': Invalid Debian package name "' +
                             self._args.args[0] + '".')
        else:
            print("usage: deb.py [-h] [-l] [-s] [-L] [-d] [-P] [-S] [-i] [-I]", file=sys.stderr)
            print("              [package.deb|package|arch [package.deb|package|arch ...]]",
                  file=sys.stderr)
            print("deb.py: error: the following arguments are required: package.deb",
                  file=sys.stderr)
            raise SystemExit(1)


class Package(syslib.Dump):

    def __init__(self, version, size, depends, description):
        self._version = version
        self._size = size
        self._depends = depends
        self._description = description

    def appendDepends(self, name):
        """
        Append to dependency list.

        name = Package name
        """
        self._depends.append(name)

    def getDepends(self):
        """
        Return depends.
        """
        return self._depends

    def setDepends(self, names):
        """
        Set package dependency list.

        names = List of package names
        """
        self._depends = names

    def getDescription(self):
        """
        Return description.
        """
        return self._description

    def setDescription(self, description):
        """
        Set description.

        description = Package description
        """
        self._description = description

    def getSize(self):
        """
        Return size.
        """
        return self._size

    def setSize(self, size):
        """
        Set size.

        size = Package size
        """
        self._size = size

    def getVersion(self):
        """
        Return version.
        """
        return self._version

    def setVersion(self, version):
        """
        Set version.

        version = Package version
        """
        self._version = version


class PackageManger(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._readDpkgStatus()

        mode = options.getMode()
        if mode == "list":
            self._showPackagesInfo()
        elif mode == "depends":
            for packagename in options.getPackageNames():
                self._showDependentPackages([packagename], checked=[])
        else:
            options.getDpkg().run(mode="exec")

    def _readDpkgStatus(self):
        namesAll = []
        self._packages = {}
        name = ""
        package = Package("", -1, [], "")
        try:
            with open("/var/lib/dpkg/status", errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip("\r\n")
                    if line.startswith("Package: "):
                        name = line.replace("Package: ", "", 1)
                    elif line.startswith("Architecture: "):
                        arch = line.replace("Architecture: ", "", 1)
                        if arch == "all":
                            namesAll.append(name)
                        elif arch != self._options.getArch():
                            name += ":" + arch
                    elif line.startswith("Version: "):
                        package.setVersion(line.replace("Version: ", "", 1).split(":")[-1])
                    elif line.startswith("Installed-Size: "):
                        try:
                            package.setSize(int(line.replace("Installed-Size: ", "", 1)))
                        except ValueError:
                            raise SystemExit(sys.argv[0] + ': Package "' + name +
                                             '" in "/var/lib/dpkg/info" has non integer size.')
                    elif line.startswith("Depends: "):
                        depends = []
                        for i in line.replace("Depends: ", "", 1).split(", "):
                            package.appendDepends(i.split()[0])
                    elif line.startswith("Description: "):
                        package.setDescription(line.replace("Description: ", "", 1))
                        self._packages[name] = package
                        package = Package("", -1, [], "")
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "/var/lib/dpkg/status" file.')

        for name, value in self._packages.items():
            if ":" in name:
                depends = []
                for depend in value.getDepends():
                    if depend.split(":")[0] in namesAll:
                        depends.append(depend)
                    else:
                        depends.append(depend + ":" + name.split(":")[-1])
                self._packages[name].setDepends(depends)

    def _showPackagesInfo(self):
        for name, package in sorted(self._packages.items()):
            if self._options.getArchSub():
                if not name.endswith(self._options.getArchSub()):
                    continue
            elif ":" in name:
                continue
            print("{0:35s} {1:15s} {2:5d}KB {3:s}".format(name.split(":")[0],
                  package.getVersion(), package.getSize(), package.getDescription()))

    def _showDependentPackages(self, names, checked=[], ident=""):
        keys = sorted(self.getPackages().keys())
        for name in names:
            if name in self.getPackages():
                print(ident + name)
                for key in keys:
                    if name in self._packages[key].getDepends():
                        if key not in checked:
                            checked.append(key)
                            checked.extend(self._showDependentPackages([key],
                                           checked, ident + "  "))
        return checked

    def _showDependentPackages(self, names, checked=[], ident=""):
        keys = sorted(self._packages.keys())
        for name in names:
            if name in self._packages:
                print(ident + name)
                for key in keys:
                    if name in self._packages[key].getDepends():
                        if key not in checked:
                            checked.append(key)
                            self._showDependentPackages([key], checked, ident + "  ")


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            PackageManger(options)
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
