#!/usr/bin/env python3
"""
Wrapper for "tinyproxy" command
"""

import getpass
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_tinyproxy(self) -> command_mod.Command:
        """
        Return tinyproxy Command class object.
        """
        return self._tinyproxy

    @staticmethod
    def _create_config() -> None:
        try:
            with Path('tinyproxy.conf').open('w') as ofile:
                print("Port 8888", file=ofile)
                print('PidFile "tinyproxy.pid"', file=ofile)
                print('LogFile "tinyproxy.log"', file=ofile)
                print("", file=ofile)
                print("##LogLevel Critical", file=ofile)
                print("##LogLevel Error", file=ofile)
                print("LogLevel Warning", file=ofile)
                print("##LogLevel Notice", file=ofile)
                print("##LogLevel Connect", file=ofile)
                print("##LogLevel Info", file=ofile)
                print("", file=ofile)
                print('ViaProxyName "tinyproxy"', file=ofile)
                print("Timeout 600", file=ofile)
                print("MaxClients 100", file=ofile)
                print("", file=ofile)
                print("# SSL", file=ofile)
                print("ConnectPort 443", file=ofile)
                print("ConnectPort 563", file=ofile)
                print("", file=ofile)
                print("# Restrict clients", file=ofile)
                print("Allow 127.0.0.1", file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "tinyproxy.conf" '
                'configuration file.',
            ) from exception

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._tinyproxy = command_mod.Command('tinyproxy', errors='stop')
        if len(args) > 1:
            self._tinyproxy.set_args(args[1:])
        elif getpass.getuser() != 'root':
            if not Path('tinyproxy.conf').is_file():
                self._create_config()
            self._tinyproxy.set_args(['-d', '-c', 'tinyproxy.conf'])


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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        subtask_mod.Exec(options.get_tinyproxy().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
