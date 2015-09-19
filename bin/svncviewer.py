#!/usr/bin/env python3
"""
Securely connect to VNC server using SSH protocol.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        try:
            remoteHost, remotePort = self._args.server[0].split(":")
        except ValueError:
            raise SystemExit(
                sys.argv[0] + ': You must specific a single ":" in VNC server location.')

        try:
            if int(remotePort) < 101:
                remotePort = str(int(remotePort) + 5900)
        except ValueError:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer "
                             "for port number.")

        self._vncviewer = syslib.Command("vncviewer")
        if remoteHost:
            localPort = self._getport(remoteHost, remotePort)
            print('Starting "vncviewer" connection via "localhost:' + localPort + '" to "' +
                  remoteHost + ":" + remotePort + '"...')
        else:
            localPort = remotePort
            print('Starting "vncviewer" connection to "localhost:' + localPort + '"...')
        self._vncviewer.setArgs([":" + localPort])

    def getVncviewer(self):
        """
        Return vncviewer Command class object.
        """
        return self._vncviewer

    def _getport(self, remoteHost, remotePort):
        lsof = syslib.Command("lsof", args=["-i", "tcp:5901-5999"])
        lsof.run(mode="batch")
        for localPort in range(5901, 6000):
            if not lsof.isMatchOutput(":" + str(localPort) + "[ -]"):
                ssh = syslib.Command("ssh", args=["-f", "-L", str(localPort) + ":localhost:" +
                                     remotePort, remoteHost, "sleep", "64"])
                print('Starting "ssh" port forwarding from "localhost:' + str(localPort) +
                      '" to "' + remoteHost + ":" + remotePort + '"...')
                ssh.run()
                return str(localPort)
        raise SystemExit(sys.argv[0] + ": Cannot find unused local port in range 5901-5999.")

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Securely connect to VNC server using SSH protocol.")

        parser.add_argument("server", nargs=1, metavar="[[user]@host]:port",
                            help="VNC server location.")

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getVncviewer().run(mode="daemon")
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
