#!/usr/bin/env python3
"""
Show files with same MD5 checksums.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import hashlib
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getRecursiveFlag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Show files with same MD5 checksums.")

        parser.add_argument("-R", dest="recursiveFlag", action="store_true",
                            help="Recursive into sub-directories.")

        parser.add_argument("files", nargs="+", metavar="file|file.md5",
                            help='File to checksum or ".md5" checksum file.')

        self._args = parser.parse_args(args)


class Md5same(syslib.Dump):

    def __init__(self, options):
        self._md5files = {}
        self._calc(options, options.getFiles())

        for md5sum in sorted(self._md5files.keys()):
            if len(self._md5files[md5sum]) > 1:
                print(syslib.Command().args2cmd(sorted(self._md5files[md5sum])))

    def _calc(self, options, files):
        for file in files:
            if os.path.isdir(file):
                if not os.path.islink(file) and options.getRecursiveFlag():
                    try:
                        self._calc(options,
                                   sorted([os.path.join(file, x) for x in os.listdir(file)]))
                    except PermissionError:
                        raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" directory.')
            elif os.path.isfile(file):
                md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
                if md5sum in self._md5files.keys():
                    self._md5files[md5sum].append(file)
                else:
                    self._md5files[md5sum] = [file]

    def _md5sum(self, file):
        try:
            with open(file, "rb") as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (IOError, TypeError):
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
        return md5.hexdigest()


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Md5same(options)
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
