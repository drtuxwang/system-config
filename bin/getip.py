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
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_hosts(self) -> List[str]:
        """
        Return list of hosts.
        """
        return self._args.hosts

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Get the IP number of hosts.',
        )

        parser.add_argument(
            'hosts',
            nargs='+',
            metavar='host',
            help='Host name.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        for host in options.get_hosts():
            try:
                ip_address = socket.gethostbyname(host)
            except socket.gaierror:
                ip_address = ''
            print(host.lower() + ':', ip_address)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
