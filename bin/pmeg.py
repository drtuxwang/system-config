#!/usr/bin/env python3
"""
Resize large picture images to mega-pixels limit.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import math
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._convert = syslib.Command("convert")

    def getConvert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def getDirectories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def getMegs(self):
        """
        Return mega-pixels.
        """
        return self._args.megs[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Resize large picture images to mega-pixels limit.")

        parser.add_argument("-megs", nargs=1, type=float, default=[9],
                            help="Select mega-pixels. Default is 9.")

        parser.add_argument("directories", nargs="+", metavar="directory",
                            help="Directory containing JPEG files to resize.")

        self._args = parser.parse_args(args)

        if self._args.megs[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive number for megabytes.")

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(sys.argv[0] + ': Image directory "' + directory +
                                 '" does not exist.')


class Remeg(syslib.Dump):

    def __init__(self, options):
        self._convert = options.getConvert()
        megs = options.getMegs()

        for directory in options.getDirectories():
            for file in sorted(glob.glob(os.path.join(directory, "*"))):
                if (file.split(".")[-1].lower() in (
                        "bmp", "gif", "jpg", "jpeg", "png", "pcx", "svg", "tif", "tiff")):
                    ix, iy = self._imagesize(options, file)
                    imegs = ix * iy / 1000000
                    print("{0:s}: {1:d} x {2:d} ({3:4.2f})".format(file, ix, iy, imegs), end="")
                    resize = math.sqrt(megs / imegs)
                    ox = int(ix*resize + 0.5)
                    oy = int(iy*resize + 0.5)
                    if ox < ix and oy < iy:
                        print(" => {0:d} x {1:d} ({2:4.2f})".format(ox, oy, ox * oy / 1000000),
                              end="")
                        self._convert.setArgs(["-verbose", "-size", str(ox) + "x" + str(oy),
                                               "-resize", str(ox) + "x" + str(oy) + "!",
                                               file, file])
                        self._convert.run(mode="batch")
                        if self._convert.getExitcode():
                            raise SystemExit(sys.argv[0] + ': Error code ' +
                                             str(self._convert.getExitcode()) + ' received from "' +
                                             self._convert.getFile() + '".')
                    print()

    def _imagesize(self, options, file):
        self._convert.setArgs(["-verbose", file, "/dev/null"])
        self._convert.run(filter="^" + file + "=>", mode="batch", error2output=True)
        if not self._convert.hasOutput():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" picture file.')
        elif self._convert.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.getExitcode()) +
                             ' received from "' + self._convert.getFile() + '".')
        x, y = self._convert.getOutput()[0].split("+")[0].split()[-1].split("x")
        return (int(x), int(y))


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Remeg(options)
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
