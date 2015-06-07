#!/usr/bin/env python3
"""
Profile Python 3.x program.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import pstats
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getFile(self):
        """
        Return list of file.
        """
        return self._args.file[0]


    def getModuleArgs(self):
        """
        Return module args.
        """
        return self._moduleArgs


    def getLines(self):
        """
        Return number of lines.
        """
        return self._args.lines[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Profile Python 3.x program.")

        parser.add_argument("-n", nargs=1, type=int, dest="lines", default=[ 20 ],
                            metavar="K", help="Output first K lines.")

        parser.add_argument("file", nargs=1, metavar="file[.py]|file.pstats",
                            help="Python module or pstats file.")

        myArgs = []
        while len(args):
            myArgs.append(args[0])
            if not args[0].startswith("-"):
                break
            elif args[0] == "-n" and len(args) >= 2:
                args = args[1:]
                myArgs.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(myArgs)

        self._moduleArgs = args[1:]


class Profiler(syslib.Dump):


    def __init__(self, options):
        self._options = options


    def run(self):
        file = self._options.getFile()

        if not file.endswith(".pstats"):
            if not file.endswith(".py"):
                file = file + ".py"
            file = self._profile(file, self._options.getModuleArgs())

        self._show(file, self._options.getLines())


    def _profile(self, moduleFile, moduleArgs):
        statsFile = os.path.basename(moduleFile.rsplit(".",1)[0] + ".pstats")

        python3 = syslib.Command(file=sys.executable)
        python3.setArgs([ "-m", "cProfile", "-o", statsFile ])

        if os.path.isfile(moduleFile):
            command = syslib.Command(file=moduleFile)
        else:
            try:
                command = syslib.Command(moduleFile)
            except syslib.SyslibError:
                raise SystemExit(
                        sys.argv[0] + ': Cannot find "' + moduleFile + '" module file')
        command.setArgs(moduleArgs)
        command.setWrapper(python3)
        command.run()

        print("pyprof:", command.args2cmd([ command.getFile() ] + moduleArgs))
        return statsFile


    def _show(self, statsFile, lines):
        try:
            stats =  pstats.Stats(statsFile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + statsFile + '" file.')

        stats.strip_dirs().sort_stats("tottime", "cumtime").print_stats(lines)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Profiler(options).run()
        except KeyboardInterrupt:
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
