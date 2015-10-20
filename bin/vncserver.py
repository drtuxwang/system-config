#!/usr/bin/env python3
"""
Wrapper for "vncserver" command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._vncserver = syslib.Command("vncserver", pathextra=["/usr/bin"])
        self._vncserver.setFlags(["-geometry", "1280x960", "-depth", "24", "-alwaysshared"])
        self._vncserver.setArgs(args[1:])
        self._umask = os.umask(int("077", 8))
        os.umask(self._umask)
        self._config()

    def getVncserver(self):
        """
        Return vncserver Command class object.
        """
        return self._vncserver

    def _config(self):
        if not os.path.isfile(os.path.join(os.environ["HOME"], ".vnc", "passwd")):
            raise SystemExit(sys.argv[0] + ': ".vnc/passwd" does not exist. Run "vncpasswd".')
        os.chdir(os.environ["HOME"])
        xstartup = os.path.join(os.environ["HOME"], ".vnc", "xstartup")
        if not os.path.isfile(xstartup):
            answer = input("Would you like to use GNOME(g), KDE(k) or XFCE(x)? ")
            try:
                with open(xstartup, "w", newline="\n") as ofile:
                    print("#!/bin/sh", file=ofile)
                    if answer[0].lower() == "g":
                        print("unset DBUS_SESSION_BUS_ADDRESS", file=ofile)
                        print("unset SESSION_MANAGER", file=ofile)
                        print("if [ -x /usr/bin/gnome-session-fallback ]; then", file=ofile)
                        print("    /usr/bin/gnome-session-fallback &", file=ofile)
                        print("elif [ -x /usr/bin/gnome-session ]; then", file=ofile)
                        print("    /usr/bin/gnome-session &", file=ofile)
                        print("else", file=ofile)
                        print("    gnome &", file=ofile)
                        print("fi", file=ofile)
                    elif answer[0].lower() == "k":
                        print("SESSION_MANAGER=; startkde &", file=ofile)
                    elif answer[0].lower() == "x":
                        print("unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS; startxfce4 &",
                              file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create ".vnc/xstartup" file.')
            os.chmod(xstartup, int("755", 8) & ~self._umask)
        directory = os.path.dirname(self._vncserver.getFile())
        if "PATH" in os.environ and directory not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] = directory + os.pathsep + os.environ["PATH"]


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getVncserver().run(mode="exec")
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
