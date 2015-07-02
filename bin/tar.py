#!/usr/bin/env python3
"""
Make a compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ|TLZ|TXZ format.
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


    def getArchive(self):
        """
        Return archive location.
        """
        return self._archive


    def getFiles(self):
        """
        Return list of files.
        """
        return self._files


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Make a compressed archive in TAR format.")

        parser.add_argument("archive", nargs=1,
                            metavar="file.tar|file.tar.gz|file.tar.bz2|file.tar.lzma|file.tar.xz|"
                                    "file.tar.7z|file.tgz|file.tbz|file.tlz|file.txz",
                            help="Archive file.")
        parser.add_argument("files", nargs="*", metavar="file",
                            help="File or directory.")

        self._args = parser.parse_args(args)

        if os.path.isdir(self._args.archive[0]):
             self._archive = os.path.abspath(self._args.archive[0]) + ".tar"
        else:
             self._archive = self._args.archive[0]
        isarchive = re.compile("[.](tar|tar[.](gz|bz2|lzma|xz|7z)|t[gblx]z)$")
        if not isarchive.search(self._archive):
            raise SystemExit(sys.argv[0] + ': Unsupported "' + self._archive + '" archive format.')

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


class Pack(syslib.Dump):


    def __init__(self, options):
        if options.getArchive().endswith(".tar"):
            try:
                self._archive = tarfile.open(options.getArchive(), "w:")
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 options.getArchive() + '" archive file.')
            self._addfile(options.getFiles())
            self._archive.close()
        else:
            tar = syslib.Command("tar")
            archive = options.getArchive()
            if archive.endswith(".tar.7z"):
                tar.setAargs([ "cfv", "-" ] + options.getFiles())
                p7zip = syslib.Command("7za")
                p7zip.setArgs([ "a", "-mx=9", "-y", "-si", archive() ])
                tar.run(pipes=[ p7zip ])
            elif archive.endswith(".txz") or archive.endswith(".tar.xz"):
                tar.setArgs([ "cfvJ", archive ] + options.getFiles())
                os.environ["XZ_OPT"] = "-9 -e"
                tar.run(mode="exec")
            else:
                tar.setArgs([ "cfva", archive ] + options.getFiles())
                os.environ["GZIP"] = "-9"
                os.environ["BZIP2"] = "-9"
                os.environ["XZ_OPT"] = "-9 -e"
                tar.run(mode="exec")


    def _addfile(self, files):
        for file in sorted(files):
            print(file)
            try:
                self._archive.add(file, recursive=False)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" file.')
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot add "' + file + '" file to archive.')
            if os.path.isdir(file):
                if not os.path.islink(file):
                    self._addfile(glob.glob(os.path.join(file, ".*")) +
                                  glob.glob(os.path.join(file, "*")))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Pack(options)
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
