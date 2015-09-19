#!/usr/bin/env python3
"""
Unpack PDF file into series of JPG files.
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

        self._gs = syslib.Command("gs")
        self._gs.setFlags(["-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=jpeg",
                           "-r" + str(self._args.dpi[0])])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getGs(self):
        """
        Return gs Command class object.
        """
        return self._gs

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Unpack PDF file into series of JPG files.")

        parser.add_argument("-dpi", nargs=1, type=int, default=[300],
                            help="Selects DPI resolution (default is 300).")

        parser.add_argument("files", nargs="+", metavar="file.pdf", help="PDF document file.")

        self._args = parser.parse_args(args)

        if self._args.dpi[0] < 50:
            raise SystemExit(sys.argv[0] + ": DPI resolution must be at least 50.")


class Unpacker(syslib.Dump):

    def __init__(self, options):
        gs = options.getGs()

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" PDF file.')
            directory = file[:-4]
            if not os.path.isdir(directory):
                try:
                    os.mkdir(directory)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + directory + '" directory.')
            print('Unpacking "' + directory + os.sep + '*.jpg" file...')
            gs.setArgs(["-sOutputFile=" + directory + os.sep + "%08d.jpg", "-c",
                        "save", "pop", "-f", file])
            gs.run(filter="Ghostscript|^Copyright|WARRANTY:|^Processing")
            if gs.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(gs.getExitcode()) +
                                 ' received from "' + gs.getFile() + '".')


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
