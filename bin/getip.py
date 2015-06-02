#!/usr/bin/env python3
"""
Get the IP number of hosts.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
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


    def getHosts(self):
        """
        Return list of hosts.
        """
        return self._args.hosts


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Get the IP number of hosts.")

        parser.add_argument("hosts", nargs="+", metavar="host", help="Host name.")

        self._args = parser.parse_args(args)


class Getip(syslib.Dump):


    def __init__(self, hosts):
        self._hosts = hosts
        self._ping = None


    def run(self):
        for host in self._hosts:
            ip = self._getIpv4(host)
            if not ip:
                ip = ""
            print(host.lower() + ":", ip)


    def _getIpv4(self, host):
        """
        Return IPv4 address.

        host = Hostname
        """
        if not self._ping:
            if os.path.isfile("/usr/sbin/ping"):
                self._ping = syslib.Command(file="/usr/sbin/ping")
            elif os.path.isfile("/usr/etc/ping"):
                self._ping = syslib.Command(file="/usr/etc/ping")
            else:
                self._ping = syslib.Command("ping")
        if os.name == "nt":
            self._ping.setArgs([ "-w", "4", "-n", "1", host ])
            self._ping.run(filter="Minimum|TTL", mode="batch")
            if self._ping.hasOutput():
                return self._ping.stdout[0].split()[2].replace(":", "")
        else:
            if syslib.info.getSystem() == "linux":
                self._ping.setArgs([ "-h" ])
                self._ping.run(filter="[-]w ", mode="batch")
                if self._ping.hasOutput():
                    self._ping.setArgs([ "-w", "4", "-c", "1", host ])
                else:
                    self._ping.setArgs([ "-c", "1", host ])
            elif syslib.info.getSystem() == "sunos":
                self._ping.setArgs([ "-s", host, "64", "1" ])
            else:
                self._ping.setArgs([ "-w", "4", "-c", "1", host ])
            self._ping.run(filter="\(.*\)", mode="batch")
            if self._ping.hasOutput():
                return self._ping.getOutput()[0].split("(")[1].split(")")[0]
        return None


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Getip(options.getHosts()).run()
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
