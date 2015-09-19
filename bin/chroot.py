#!/usr/bin/env python3
"""
Wrapper for "chroot" command
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
        if len(args) != 2 or not os.path.isdir(args[1]):
            chroot = syslib.Command("chroot", args=args[1:])
            chroot.run(mode="exec")
        elif syslib.info.getUsername() != "root":
            sudo = syslib.Command("sudo", args=["python3", args[0], os.path.abspath(args[1])])
            sudo.run(mode="exec")
        if not os.path.isfile(os.path.join(args[1], "bin", "bash")):
            raise SystemExit(sys.argv[0] + ': Cannot find "/bin/bash" in chroot directory.')
        self._directory = os.path.abspath(args[1])

    def getDirectory(self):
        """
        Return directory.
        """
        return self._directory


class Chroot(syslib.Dump):

    def __init__(self, directory):
        self._chroot = syslib.Command("/usr/sbin/chroot")
        self._chroot.setArgs([directory, "/bin/bash", "-l"])
        self._directory = directory
        self._mount = syslib.Command("mount")
        self._mountpoints = []
        self._mountDir("-o", "bind", "/dev", os.path.join(self._directory, "dev"))
        self._mountDir("-o", "bind", "/proc", os.path.join(self._directory, "proc"))
        if os.path.isdir("/shared") and os.path.isdir(os.path.join(self._directory, "shared")):
            self._mountDir("-o", "bind", "/shared", os.path.join(self._directory, "shared"))
        self._mountDir("-t", "tmpfs", "-o", "size=256m,noatime,nosuid,nodev", "tmpfs",
                       os.path.join(self._directory, "tmp"))
        if (os.path.isdir("/var/run/dbus") and
                os.path.isdir(os.path.join(self._directory, "var/run/dbus"))):
            self._mountDir("-o", "bind", "/var/run/dbus",
                           os.path.join(self._directory, "var/run/dbus"))

    def _getterm(self):
        term = "Unkown"
        if "TERM" in os.environ.keys():
            term = os.environ["TERM"]
        return term

    def _mountDir(self, *args):
        self._mount.setArgs(list(args))
        self._mount.run()
        self._mountpoints.append(args[-1])

    def run(self):
        print('Chroot "' + self._directory + '" starting...')
        if self._getterm() in ["xterm", "xvt100"]:
            sys.stdout.write("\033]0;" + syslib.info.getHostname() + ":" + self._directory + "\007")
            sys.stdout.flush()
        self._chroot.run()
        if self._getterm() in ["xterm", "xvt100"]:
            sys.stdout.write("\033]0;" + syslib.info.getHostname() + ":\007")
        syslib.Command("umount", args=["-l"] + self._mountpoints).run()
        print('Chroot "' + self._directory + '" finished!')


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Chroot(options.getDirectory()).run()
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
