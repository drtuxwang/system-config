#!/usr/bin/env python3
"""
Generate "index.xhtml" & "index.fsum" files plus "..fsum" cache files
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import hashlib
import os
import re
import shutil
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._archive = os.path.basename(os.getcwd())


    def getArchive(self):
        """
        Return archive directory.
        """
        return self._archive


class Index(syslib.Dump):


    def __init__(self, options):
        self._options = options


    def run(self):
        self._coreFind()
        self._checksum()


    def _checksum(self):
        print('Generating "index.fsum"...')
        try:
            with open("index.fsum", "a", newline="\n") as ofile:
                self._readFsums(ofile, "")
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "index.fsum" file.')

        fsum = syslib.Command("fsum")
        files = glob.glob("*")
        if "index.fsum" in files:
            files.remove("index.fsum")
            fsum.setArgs([ "-R", "-update=index.fsum" ] + files)
        else:
            fsum.setArgs([ "-R" ] + files)
        fsum.run(mode="batch")

        self._writeFsums(fsum.getOutput())
        timeNew = 0
        try:
            with open("index.fsum", "w", newline="\n") as ofile:
               for line in fsum.getOutput():
                   timeNew = max(timeNew, int(line.split(" ", 1)[0].rsplit("/", 1)[-1]))
                   print(line, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "index.fsum" file.')
        os.utime("index.fsum", (timeNew, timeNew))


    def _coreFind(self, directory=""):
        for file in sorted(glob.glob(os.path.join(directory, ".*")) +
                glob.glob(os.path.join(directory, "*"))):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    self._coreFind(file)
                elif os.path.basename(file) == "core" or os.path.basename(file).startswith("core."):
                    raise SystemExit(sys.argv[0] + ': Found "' + file + '" crash dump file.')


    def _readFsums(self, ofile, directory):
        fsum = os.path.join(directory, "..fsum")
        if directory and os.listdir(directory) == [ "..fsum" ]:
            try:
                os.remove(fsum)
            except OSError:
                pass
        else:
            try:
                with open(fsum, errors="replace") as ifile:
                    for line in ifile:
                        checksum, file = line.rstrip("\r\n").split("  ", 1)
                        print(checksum + "  " + os.path.join(directory, file), file=ofile)
            except (IOError, ValueError):
                pass
            for file in glob.glob(os.path.join(directory, "*")):
                if os.path.isdir(file) and not os.path.islink(file):
                    self._readFsums(ofile, file)


    def _writeFsums(self, lines):
        fsums = {}
        for line in lines:
            checksum, file = line.split("  ", 1)
            directory = os.path.dirname(file)
            if directory not in fsums.keys():
                fsums[directory] = []
            fsums[os.path.dirname(file)].append(checksum + "  " + os.path.basename(file))

        directories = {}
        for directory in sorted(fsums.keys()):
            depth = directory.count(os.sep)
            if depth not in directories.keys():
                directories[depth] = [ directory ]
            directories[depth].append(directory)

        for depth in sorted(directories.keys(), reverse=True):
            for directory in directories[depth]:
                file = os.path.join(directory, "..fsum")
                timeNew = 0
                try:
                    with open(file, "w", newline="\n") as ofile:
                        for line in fsums[directory]:
                            timeNew = max(timeNew, int(line.split(" ", 1)[0].rsplit("/", 1)[-1]))
                            print(line, file=ofile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')
                os.utime(file, (timeNew, timeNew))
                if directory:
                    os.utime(directory, (timeNew, timeNew))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Index(options).run()
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
