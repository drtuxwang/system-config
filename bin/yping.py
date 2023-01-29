#!/usr/bin/env python3
"""
Ping a host until a connection is made.
"""

import argparse
import os
import signal
import sys
import time
from pathlib import Path
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

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_ping(self) -> command_mod.Command:
        """
        Return ping Command class object.
        """
        return self._ping

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Ping a host until a connection is made.",
        )

        parser.add_argument('host', nargs=1, help="Host name or IP address.")

        self._args = parser.parse_args(args)

    @staticmethod
    def _get_ping() -> command_mod.Command:
        if Path('/usr/sbin/ping').is_file():
            return command_mod.CommandFile('/usr/sbin/ping')
        if Path('/usr/etc/ping').is_file():
            return command_mod.CommandFile('/usr/etc/ping')
        return command_mod.Command('ping')

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        host = self._args.host[0]
        self._ping = self._get_ping()
        self._ping.set_args(['-w', '4', '-c', '3', host])
        self._pattern = 'min/avg/max'

        if os.name == 'nt':
            self._ping.set_args(['-w', '4', '-n', '3', host])
            self._pattern = 'Minimum|TTL'
        else:
            osname = os.uname()[0]
            if osname == 'Darwin':
                self._ping.set_args(['-t', '4', '-c', '3', host])
            elif osname == 'Linux':
                self._ping.set_args(['-w', '4', '-c', '3', host])
            elif osname == 'SunOS':
                self._ping.set_args(['-s', host, '64', '3'])


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

        task = subtask_mod.Batch(options.get_ping().get_cmdline())
        while True:
            task.run(pattern=options.get_pattern())
            if task.has_output():
                break
            time.sleep(5)
        print(task.get_output()[-1].strip())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
