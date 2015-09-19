#!/usr/bin/env python3
"""
Make a compressed archive in TAR.BZ2 format.
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
        parser = argparse.ArgumentParser(description="Make a compressed archive in TAR.BZ2 format.")

        parser.add_argument("archive", nargs=1, metavar="file.tar.bz2|file.tbz",
                            help="Archive file.")
        parser.add_argument("files", nargs="*", metavar="file",
                            help="File or directory.")

        self._args = parser.parse_args(args)

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + ".tar.bz2"
        else:
            self._archive = self._args.archive[0]
        if not self._archive.endswith(".tar.bz2") and not self._archive.endswith(".tbz"):
            raise SystemExit(sys.argv[0] + ': Unsupported "' + self._archive + '" archive format.')

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


class Pack(syslib.Dump):

    def __init__(self, options):
        try:
            self._archive = tarfile.open(options.getArchive(), "w:bz2")
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' +
                             options.getArchive() + '" archive file.')
        self._addfile(options.getFiles())

    def _addfile(self, files):
        for file in sorted(files):
            print(file)
            try:
                self._archive.add(file, recursive=False)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot add "' + file + '" file to archive.')
            if os.path.isdir(file) and not os.path.islink(file):
                try:
                    self._addfile([os.path.join(file, x) for x in os.listdir(file)])
                except PermissionError:
                    raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" directory.')


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
        except SystemExit as exception:
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
