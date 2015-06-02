#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.
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
import tarfile

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
        parser = argparse.ArgumentParser(
                description="Unpack a compressed archive in "
                            "TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.")

        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Show contents of archive.")

        parser.add_argument("archives", nargs="+",
                            metavar="file.tar|file.tar.gz|file.tar.bz2|file.tar.lzma|file.tar.xz|"
                                    "file.tar.7z|file.tgz|file.tbz|file.tlz|file.txz",
                            help="Archive file.")

        self._args = parser.parse_args(args)

        isarchive = re.compile("[.](tar|tar[.](gz|bz2|lzma|xz|7z)|t[gblx]z)$")
        for archive in self._args.archives:
            if not isarchive.search(archive):
                raise SystemExit(sys.argv[0] + ': Unsupported "' + archive +'" archive format.')


class Unpack(syslib.Dump):


    def __init__(self, options):
        os.umask(int("022", 8))
        if os.name == "nt":
            self._tar = syslib.Command("tar.exe")
        else:
            self._tar = syslib.Command("tar")
        for archive in options.getArchives():
            print(archive + ":")
            if options.getViewFlag():
                self._view(archive)
            else:
                self._unpack(archive)


    def _unpack(self, archive):
        if archive.endswith(".tar.7z"):
            p7zip = syslib.Command("7za")
            p7zip.setArgs([ "x", "-y", "-so", archive ])
            self._tar.setArgs([ "xfv", "-" ])
            p7zip.run(pipes=[ self._tar ])
        else:
            self._tar.setArgs([ "xfv", archive ])
            self._tar.run()


    def _view(self, archive):
        if archive.endswith(".tar.7z"):
            p7zip = syslib.Command("7za")
            p7zip.setArgs([ "x", "-y", "-so", archive ])
            self._tar.setArgs([ "tfv", "-" ])
            p7zip.run(pipes=[ self._tar ])
        else:
            self._tar.setArgs([ "tfv", archive ])
            self._tar.run()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unpack(options)
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
