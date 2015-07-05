#!/usr/bin/env python3
"""
Show summary of differences between two directories recursively.
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


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Show summary of differences between two directories recursively.")

        parser.add_argument("directories", nargs=2, metavar="directory",
                            help="Directory to compare.")

        self._args = parser.parse_args(args)


    def getDirectory1(self):
        """
        Return directory 1.
        """
        return self._args.directories[0]


    def getDirectory2(self):
        """
        Return directory 2.
        """
        return self._args.directories[1]


class Diff(syslib.Dump):


    def __init__(self, options):
        self._diffdir(options.getDirectory1(), options.getDirectory2())


    def _diffdir(self, directory1, directory2):
        try:
            files1 = sorted([ os.path.join(directory1, x) for x in os.listdir(directory1) ])
        except (FileNotFoundError, PermissionError):
            raise SystemExit(sys.argv[0] + ': Cannot open "' + directory1 + '" directory.')

        try:
            files2 = sorted([ os.path.join(directory2, x) for x in os.listdir(directory2) ])
        except (FileNotFoundError, PermissionError):
            raise SystemExit(sys.argv[0] + ': Cannot open "' + directory2 + '" directory.')

        for file in files1:
            if os.path.isdir(file):
                if os.path.isdir(os.path.join(directory2, os.path.basename(file))):
                    self._diffdir(file, os.path.join(directory2, os.path.basename(file)))
                else:
                    print("only ", file + os.sep)
            elif os.path.isfile(file):
                if os.path.isfile(os.path.join(directory2, os.path.basename(file))):
                    self._difffile(file, os.path.join(directory2, os.path.basename(file)))
                else:
                    print("only ", file)

        for file in files2:
            if os.path.isdir(file):
                if not os.path.isdir(os.path.join(directory1, os.path.basename(file))):
                    print("only ", file + os.sep)
            elif os.path.isfile(file):
                if not os.path.isfile(os.path.join(directory1, os.path.basename(file))):
                    print("only ", file)


    def _difffile(self, file1, file2):
        fileStat1 = syslib.FileStat(file1)
        fileStat2 = syslib.FileStat(file2)

        if (fileStat1.getSize() != fileStat2.getSize()):
            print("diff ", file1 + "  " + file2)
        elif (fileStat1.getTime() != fileStat2.getTime()):
            try:
                ifile1 = open(file1, "rb")
            except IOError:
                print("diff ", file1 + "  " + file2)
                return
            try:
                ifile2 = open(file2, "rb")
            except IOError:
                print("diff ", file1 + "  " + file2)
                return
            for i in range(0, fileStat1.getSize(), 131072):
                chunk1 = ifile1.read(131072)
                chunk2 = ifile2.read(131072)
                if chunk1 != chunk2:
                    print("diff ", file1 + "  " + file2)
                    return
            ifile1.close()
            ifile2.close()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Diff(options)
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
