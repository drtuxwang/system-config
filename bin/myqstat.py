#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job statistics.

"""

RELEASE = "2.6.0"

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])


    def getRelease(self):
        """
        Return release version.
        """
        return self._release


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="MyQS v" + self._release + ", My Queuing System batch job submission.")

        self._args = parser.parse_args(args)


class Sorter(syslib.Dump):


    def __init__(self, x, *args):
        self._x = x


    def __cmp__(self, y):
        cmp = int(x.split("/")[-1][:-2]) - int(y.split("/")[-1][:-2])
        if cmp > 0:
            return 1
        elif cmp < 0:
            return -1
        else:
            return 0


class Stats(syslib.Dump):


    def __init__(self, options):
        hostname = syslib.info.getHostname()
        print('\nMyQS', options.getRelease(),
                ', My Queuing System batch job statistics on HOST "' + hostname + '".\n')
        if "HOME" not in os.environ.keys():
            raise SystemExit(sys.argv[0] + ": Cannot determine home directory.")
        self._myqsdir = os.path.join(os.environ["HOME"], ".config",
                                     "myqs", syslib.info.getHostname())
        self._showjobs()
        self._myqsd()


    def _myqsd(self):
        lockfile = os.path.join(self._myqsdir, "myqsd.pid")
        try:
            with open(lockfile, errors="replace") as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (IOError, ValueError):
                    pass
                else:
                    if syslib.Task().haspid(pid):
                        return
                    else:
                        os.remove(lockfile)
        except IOError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')


    def _showjobs(self):
        print("JOBID  QUEUENAME  JOBNAME                                     CPUS  STATE  TIME")
        jobids = []
        for file in glob.glob(os.path.join(self._myqsdir, "*.[qr]")):
            try:
                jobids.append(int(os.path.basename(file)[:-2]))
            except ValueError:
                pass
        for jobid in sorted(jobids):
            try:
                ifile = open(os.path.join(self._myqsdir, str(jobid) + ".q"), errors="replace")
            except IOError:
                try:
                    ifile = open(os.path.join(self._myqsdir, str(jobid) + ".r"), errors="replace")
                except IOError:
                    continue
                state = "RUN"
            else:
                state = "QUEUE"
            info = {}
            for line in ifile:
                line = line.strip()
                if "=" in line:
                    info[line.strip().split("=")[0]] = line.split("=", 1)[1]
            ifile.close()
            if "NCPUS" in info.keys():
                output = []
                if "START" in info.keys():
                    try:
                        etime = str(int((time.time()-float(info["START"]))/60.))
                        pgid = int(info["PGID"])
                    except ValueError:
                        etime = "0"
                    else:
                        if syslib.Task().haspgid(pgid):
                            if os.path.isdir(info["DIRECTORY"]):
                                logfile = os.path.join(info["DIRECTORY"],
                                        os.path.basename(info["COMMAND"]) + ".o" + str(jobid))
                            else:
                                logfile = os.path.join(os.environ["HOME"],
                                        os.path.basename(info["COMMAND"]) + ".o" + str(jobid))
                            try:
                                with open(logfile, errors="replace") as ifile:
                                    output = []
                                    for line in ifile:
                                        output = (output + [ line.rstrip() ])[-5:]
                            except IOError:
                                pass
                        else:
                            state = "STOP"
                else:
                    etime = "-"
                print("{0:5d}  {1:9s}  {2:42s}  {3:>3s}   {4:5s} {5:>5s}".format(
                      jobid, info["QUEUE"], info["COMMAND"], info["NCPUS"], state, etime))
                for line in output:
                    print(line)
        print()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Stats(options)
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
