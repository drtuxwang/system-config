#!/usr/bin/env python3
"""
Make a Python3 ZIP Application in PYZ format.
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

        if os.name == "nt":
            self._archiver = syslib.Command("pkzip32.exe", check=False)
            if self._archiver.isFound():
                self._archiver.setFlags(
                        [ "-add", "-maximum", "-recurse", "-path", self._args.archive[0] + "-zip" ])
            else:
                self._archiver = syslib.Command(
                        "zip", flags=[ "-r", "-9", self._args.archive[0] + "-zip" ])
        else:
            self._archiver = syslib.Command(
                    "zip", flags=[ "-r", "-9", self._args.archive[0] + "-zip" ])

        if self._args.files:
            self._archiver.setArgs(self._args.files)
        else:
            self._archiver.setArgs(glob.glob(".*") + glob.glob("*"))

        if "__main__.py" not in self._archiver.getArgs():
            raise SystemExit(sys.argv[0] + ': Cannot find "__main__.py" main program file.')


    def getArchive(self):
        """
        Return archive location.
        """
        return self._args.archive


    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Make a Python3 ZIP Application in PYZ format.")

        parser.add_argument("archive", nargs=1, metavar="file.pyz", help="Archive file.")
        parser.add_argument("files", nargs="*", metavar="file", help="File to archive.")

        self._args = parser.parse_args(args)


class Pack(syslib.Dump):


    def __init__(self, options):
        archiver = options.getArchiver()

        archiver.run()
        if archiver.getExitcode():
            print(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) + ' received from "' +
                  archiver.getFile() + '".', file = sys.stderr)
            raise SystemExit(archiver.getExitcode())
        self._makePyz(options.getArchive())


    def _makePyz(self, archive):
        try:
            with open(archive, "wb") as ofile:
                ofile.write(b"#!/usr/bin/env python3\n")
                with open(archive + "-zip", "rb") as ifile:
                    self._copy(ifile, ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + archive +
                             '" Python3 ZIP Application.')
        try:
            os.remove(archive + "-zip")
        except OSError:
            pass
        os.chmod(archive, int("755", 8))


    def _copy(self, ifile, ofile):
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)


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
