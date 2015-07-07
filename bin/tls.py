#!/usr/bin/env python3
"""
Show all tasks belonging to an user.
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

        if self._args.username:
            self._task = syslib.Task(self._args.username)
        elif self._args.allFlag:
            self._task = syslib.Task("<all>")
        else:
            self._task = syslib.Task()


    def getTask(self):
        """
        Return task Task class object.
        """
        return self._task


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Show all tasks belonging to an user.")

        parser.add_argument("-a", dest="allFlag", action="store_true",
                            help="Show task list for all users.")

        parser.add_argument("username", nargs="?", help="user name.")

        self._args = parser.parse_args(args)


class Show(syslib.Dump):


    def __init__(self, task):
        try:
            print("RUSER      PID  PPID  PGID PRI  NI TTY      MEMORY  CPUTIME     ELAPSED COMMAND")
            for pid in task.getPids():
                process = task.getProcess(pid)
                print("{0:8s} {1:5d} {2:5d} {3:5d} {4:>3s} {5:>3s} {6:7s} {7:7d} {8:>8s} "
                      "{9:>11s} {10:s}".format(process["USER"].split()[0], pid, process["PPID"],
                      process["PGID"], process["PRI"], process["NICE"], process["TTY"],
                      process["MEMORY"], process["CPUTIME"], process["ETIME"], process["COMMAND"]))
        except IOError:
            pass


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Show(options.getTask())
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
