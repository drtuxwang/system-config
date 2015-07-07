#!/usr/bin/env python3
"""
Download Debian packages list files.
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


    def getDistributionFiles(self):
        """
        Return list of distribution files.
        """
        return self._args.distributionFiles


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Download Debian packages list files.")

        parser.add_argument("distributionFiles", nargs="+", metavar="distribution.dist",
                            help="File containing Debian package URLs.")

        self._args = parser.parse_args(args)


class Distribution(syslib.Dump):


    def __init__(self, options):
        self._wget = syslib.Command("wget", flags=[ "--timestamping" ])
        os.umask(int("022", 8))
        for distributionFile in options.getDistributionFiles():
            if distributionFile.endswith(".dist"):
                try:
                    print('Checking "' + distributionFile + '" distribution file...')
                    lines = []
                    with open(distributionFile, errors="replace") as ifile:
                        for url in ifile:
                            url = url.rstrip()
                            if url and not url.startswith("#"):
                                lines.extend(self._getPackageList(url))
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' +
                                     distributionFile + '" distribution file.')
                try:
                    file = distributionFile[:-4] + "packages"
                    with open(file + "-new", "w", newline="\n") as ofile:
                        for line in lines:
                            print(line, file=ofile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '-new" file.')
                try:
                    os.rename(file + "-new", file)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')


    def _getPackageList(self, url):
        archive = os.path.basename(url)
        if not url.startswith("http://") or archive not in (
                "Packages.xz", "Packages.bz2", "Packages.gz" ):
            raise SystemExit(sys.argv[0] + ': Invalid "' + url + '" URL.')
        self._remove()
        self._wget.setArgs([ url ])
        self._wget.run(mode="batch")
        if self._wget.isMatchError(" saved "):
            print("  [" + syslib.FileStat(archive).getTimeLocal() + "]", url)
        elif not self._wget.isMatchError("^Server file no newer"):
            print("  [File Download Error]", url)
            self._remove()
            raise SystemExit(1)
        elif self._wget.getExitcode():
            self._remove()
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._wget.getExitcode()) +
                             ' received from "' + wget.getFile() + '".')
        self._unpack(archive)
        site = url[:url.find("/dists/") + 1]
        lines = []
        try:
            with open("Packages", errors="replace") as ifile:
                for line in ifile:
                    if line.startswith("Filename: "):
                        lines.append(line.rstrip("\r\n").replace(
                                "Filename: ", "Filename: " + site, 1))
                    else:
                        lines.append(line.rstrip("\r\n"))
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "Packages" packages file.')
        self._remove()
        return lines


    def _remove(self):
        try:
            os.remove("Packages")
            os.remove("Packages.bz2")
        except OSError:
            pass


    def _unpack(self, file):
        if file.endswith(".xz"):
            syslib.Command("xz", args=[ "-d", file ]).run()
        elif file.endswith(".bz2"):
            syslib.Command("bzip2", args=[ "-d", file ]).run()
        elif file.endswith(".gz"):
            syslib.Command("gzip", args=[ "-d", file ]).run()
        else:
            raise SystemExit(sys.argv[0] + ': Cannot unpack "' + file + '" package file.')


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Distribution(options)
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
