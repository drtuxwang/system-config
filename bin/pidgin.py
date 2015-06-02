#!/usr/bin/env python3
"""
Wrapper for "pidgin" command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._pidgin = syslib.Command("pidgin")
        self._pidgin.setArgs(args[1:])
        self._config()


    def getPidgin(self):
        """
        Return pidgin Command class object.
        """
        return self._pidgin


    def _config(self):
        if "HOME" in os.environ.keys():
            configdir = os.path.join(os.environ["HOME"], ".purple")
            configfile = os.path.join(configdir, "prefs.xml")
            try:
                with open(configfile, errors="replace") as ifile:
                    try:
                        with open(configfile + "-new", "w", newline="\n") as ofile:
                            # Disable logging of chats
                            islog = re.compile("log_.*type='bool'")
                            for line in ifile:
                                if islog.search(line):
                                    line = line.rstrip().replace("1", "0")
                                print(line, file=ofile)
                    except IOError:
                        return
            except IOError:
                return
            try:
                os.rename(configfile + "-new", configfile)
            except OSError:
                pass


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getPidgin().run(mode="background")
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
