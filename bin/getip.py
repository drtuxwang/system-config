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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_hosts(self):
        """
        Return list of hosts.
        """
        return self._args.hosts

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Get the IP number of hosts.')

        parser.add_argument('hosts', nargs='+', metavar='host', help='Host name.')

        self._args = parser.parse_args(args)


class Getip(object):
    """
    Get IP address class
    """

    def __init__(self, hosts):
        self._hosts = hosts

    def run(self):
        """
        Determin IP address
        """
        for host in self._hosts:
            try:
                ip_address = socket.gethostbyname(host)
            except socket.gaierror:
                ip_address = ''
            print(host.lower() + ':', ip_address)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Getip(options.get_hosts()).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
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
