#!/usr/bin/env python3
"""
Automatic connection to FTP server anonymously.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_ftp(self) -> command_mod.Command:
        """
        Return ftp Command class object.
        """
        return self._ftp

    @staticmethod
    def _netrc(host: str) -> None:
        netrc = os.path.join(os.environ.get('HOME', ''), '.netrc')
        umask = os.umask(int('077', 8))
        try:
            with open(netrc, 'w', newline='\n') as ofile:
                print(
                    "machine",
                    host,
                    "login anonymous password "
                    "someone@somehost.somecompany.com",
                    file=ofile
                )
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + netrc +
                '" configuration file.'
            ) from exception
        os.umask(umask)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Automatic connection to FTP server anonymously.')

        parser.add_argument('host', nargs=1, help='Ftp host.')

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._ftp = command_mod.Command('ftp', errors='stop')
        self._ftp.set_args(['-i', self._args.host[0]])

        self._netrc(self._args.host[0])


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

        subtask_mod.Exec(options.get_ftp().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
