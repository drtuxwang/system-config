#!/usr/bin/env python3
"""
Get the IP number of hosts.
"""

import argparse
import glob
import os
import signal
import socket
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getHosts(self):
        """
        Return list of hosts.
        """
        return self._args.hosts

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Get the IP number of hosts.')

        parser.add_argument('hosts', nargs='+', metavar='host', help='Host name.')

        self._args = parser.parse_args(args)


class Getip:

    def __init__(self, hosts):
        self._hosts = hosts

    def run(self):
        for host in self._hosts:
            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                ip = ''
            print(host.lower() + ':', ip)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
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
        if hasattr(signal, 'SIGPIPE'):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
