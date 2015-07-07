#!/usr/bin/env python3
"""
Unpack an encrypted archive in gpg (pgp compatible) format.
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

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self._gpg = syslib.Command("gpg")

        self._config()
        self._setLibraries(self._gpg)


    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files


    def getGpg(self):
        """
        Return gpg Command class object.
        """
        return self._gpg


    def _config(self):
        if "HOME" in os.environ.keys():
            os.umask(int("077", 8))
            gpgdir = os.path.join(os.environ["HOME"], ".gnupg")
            if not os.path.isdir(gpgdir):
                try:
                    os.mkdir(gpgdir)
                except OSError:
                    return
            try:
                os.chmod(gpgdir, int("700", 8))
            except OSError:
                return
        if "DISPLAY" in os.environ.keys():
            os.environ["DISPLAY"] = ""


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Unpack an encrypted archive in gpg (pgp compatible) format.")

        parser.add_argument("files", nargs="+", metavar="file.gpg|file.pgp",
                            help="GPG/PGP encrypted file.")

        self._args = parser.parse_args(args)


    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), "lib")
        if os.path.isdir(libdir):
            if syslib.info.getSystem() == "linux":
                if "LD_LIBRARY_PATH" in os.environ.keys():
                    os.environ["LD_LIBRARY_PATH"] = (
                            libdir + os.pathsep + os.environ["LD_LIBRARY_PATH"])
                else:
                    os.environ["LD_LIBRARY_PATH"] = libdir


class Ungpg(syslib.Dump):


    def __init__(self, options):
        gpg = options.getGpg()

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            gpg.setArgs([ file ])
            gpg.run()
            if gpg.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(gpg.getExitcode()) +
                                 ' received from "' + gpg.getFile() + '".')


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Ungpg(options)
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
