#!/usr/bin/env python3
"""
Wrapper for "rpm" command (adds "rpm -l")
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._rpm = syslib.Command("rpm")
        if len(args) == 1 or args[1] != "-l":
            self._rpm.setArgs(sys.argv[1:])
            self._rpm.run(mode="exec")

        self._mode = "show_packages_info"

    def getMode(self):
        """
        Return operation mode.
        """
        return self._mode

    def getRpm(self):
        """
        Return rpm Command class object.
        """
        return self._rpm


class Package(syslib.Dump):

    def __init__(self, version, size, description):
        self._version = version
        self._size = size
        self._description = description

    def getDescription(self):
        """
        Return package description.
        """
        return self._description

    def setDescription(self, description):
        """
        Set package description.

        description = Package description
        """
        self._description = description

    def getSize(self):
        """
        Return package size.
        """
        return self._size

    def setSize(self, size):
        """
        Set package size.

        size = Package size
        """
        self._size = size

    def getVersion(self):
        """
        Return package version.
        """
        return self._version

    def setVersion(self, version):
        """
        Set package version.

        version = Package version
        """
        self._version = version


class PackageManger(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._readRpmStatus()

        self._showPackagesInfo()

    def _readRpmStatus(self):
        rpm = self._options.getRpm()
        rpm.setArgs(["-a", "-q", "-i"])
        rpm.run(mode="batch")
        name = ""
        self._packages = {}
        package = Package("", -1, "")

        for line in rpm.getOutput():
            if line.startswith("Name "):
                name = line.split()[2]
            elif line.startswith("Version "):
                package.setVersion(line.split()[2])
            elif line.startswith("Size "):
                try:
                    package.setSize(int((int(line.split()[2]) + 1023) / 1024))
                except ValueError:
                    raise SystemExit(sys.argv[0] + ': Package "' + name + '" has non integer size.')
            elif line.startswith("Summary "):
                package.setDescription(line.split(": ")[1])
                self._packages[name] = package
                package = Package("", "0", "")
        return

    def _showPackagesInfo(self):
        for name in sorted(self._packages.keys()):
            print("{0:35s} {1:15s} {2:5d}KB {3:s}".format(name.split(":")[0],
                  self._packages[name].getVersion(), self._packages[name].getSize(),
                  self._packages[name].getDescription()))


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
