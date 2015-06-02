#!/usr/bin/env python3
"""
Unpack a compressed archive in DEB format.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
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


    def getArchives(self):
        """
        Return list of archives.
        """
        return self._args.archives


    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Unpack a compressed archive in DEB format.")

        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Show contents of archive.")

        parser.add_argument("archives", nargs="+", metavar="file.deb", help="Archive file.")

        self._args = parser.parse_args(args)


class Unpacker(syslib.Dump):


    def __init__(self, options):
        os.umask(int("022", 8))
        self._options = options
        self._ar = syslib.Command("ar")
        self._p7zip = syslib.Command("7za", flags=[ "x" ])
        if options.getViewFlag():
            self._tar = syslib.Command("tar", flags=[ "tf" ])
        else:
            self._tar = syslib.Command("tar", flags=[ "xvf" ])
        for file in options.getArchives():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" DEB file.')
            self._unpack(file)


    def _unpack(self, file):
        self._ar.setArgs([ "tv", file ])
        self._ar.run(filter="data.tar", mode="batch")
        if len(self._ar.getOutput()) != 1:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" DEB file.')
        elif self._ar.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.getExitcode()) +
                             ' received from "' + self._ar.getFile() + '".')
        archive = self._ar.getOutput()[-1].split()[-1]
        self._remove(archive, "data.tar")
        self._ar.setArgs([ "x", file, archive ])
        self._ar.run()
        if self._ar.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.getExitcode()) +
                             ' received from "' + self._ar.getFile() + '".')
        self._p7zip.setArgs([ archive ])
        self._p7zip.run(mode="batch")
        if self._p7zip.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._p7zip.getExitcode()) +
                             ' received from "' + self._p7zip.getFile() + '".')
        self._tar.setArgs([ "data.tar" ])
        self._tar.run()
        if self._tar.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._tar.getExitcode()) +
                             ' received from "' + self._tar.getFile() + '".')
        self._remove(archive, "data.tar")
        self._ar.setArgs([ "x", file, "control.tar.gz" ])
        self._ar.run()
        if self._ar.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.getExitcode()) +
                             ' received from "' + self._ar.getFile() + '".')
        if not self._options.getViewFlag() and not os.path.isdir("DEBIAN"):
            try:
                os.mkdir("DEBIAN")
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "DEBIAN" directory.')
        if os.path.isdir("DEBIAN"):
            self._tar.setArgs([ os.path.join(os.pardir, "control.tar.gz") ])
            self._tar.run(directory="DEBIAN", replace=(os.curdir, "DEBIAN"))
        else:
            self._tar.setArgs([ "control.tar.gz" ])
            self._tar.run(replace=(os.curdir, "DEBIAN"))
        if self._tar.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._tar.getExitcode()) +
                             ' received from "' + self._tar.getFile() + '".')
        self._remove("control.tar.gz")


    def _remove(self,*files):
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unpacker(options)
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
