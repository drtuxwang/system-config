#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.BZ2 format.
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
                description="Unpack a compressed archive in TAR.BZ2 format.")

        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Show contents of archive.")

        parser.add_argument("archives", nargs="+", metavar="file.tar.bz2|file.tbz",
                            help="Archive file.")

        self._args = parser.parse_args(args)

        for archive in self._args.archives:
            if not archive.endswith(".tar.bz2") and not archive.endswith(".tbz"):
                raise SystemExit(sys.argv[0] + ': Unsupported "' + archive +'" archive format.')


class Unpack(syslib.Dump):


    def __init__(self, options):
        os.umask(int("022", 8))
        for archive in options.getArchives():
            print(archive + ":")
            try:
                self._archive = tarfile.open(archive, "r:bz2")
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot open "' + archive + '" archive file.')
            if options.getViewFlag():
                self._view()
            else:
                self._unpack()


    def _unpack(self):
        for file in self._archive.getnames():
            print(file)
            if os.path.isabs(file):
                raise SystemExit(sys.argv[0] + ": Unsafe to extract file with absolute outside "
                                               "of current directory.")
            elif file.startswith(os.pardir):
                raise SystemExit(sys.argv[0] + ": Unsafe to extract file with relative path "
                                               "outside of current directory.")
            try:
                self._archive.extract(self._archive.getmember(file))
            except (IOError, OSError):
                raise SystemExit(sys.argv[0] + ': Unable to create "' + file + '" extracted.')
            if not os.path.isfile(file):
                if not os.path.isdir(file):
                    if not os.path.islink(file):
                        raise SystemExit(sys.argv[0] +
                                         ': Cannot create extracted "' + file + '" file.')


    def _view(self):
        self._archive.list()


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
        except SystemExit as exception:
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
