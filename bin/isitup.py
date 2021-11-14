#!/usr/bin/env python3
"""
Checks whether a host is up.
"""

import argparse
import glob
import os
import signal
import sys
import time
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

    def get_host(self) -> str:
        """
        Return host.
        """
        return self._args.host[0]

    def get_ping(self) -> command_mod.Command:
        """
        Return ping Command class object.
        """
        return self._ping

    def get_repeat_flag(self) -> bool:
        """
        Return repeat flag.
        """
        return self._args.repeat_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Checks whether a host is up.",
        )

        parser.add_argument(
            '-f',
            dest='repeat_flag',
            action='store_true',
            help="Monitor host every five seconds.",
        )
        parser.add_argument(
            'host',
            nargs=1,
            help="Host to monitor.",
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _get_ping() -> command_mod.Command:
        if os.path.isfile('/usr/sbin/ping'):
            return command_mod.CommandFile('/usr/sbin/ping')
        if os.path.isfile('/usr/etc/ping'):
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
            if osname == 'Linux':
                task = subtask_mod.Batch(self._ping.get_cmdline() + ['-h'])
                task.run(pattern='[-]w ')
                if task.has_output():
                    self._ping.set_args(['-w', '4', '-c', '3', host])
                else:
                    self._ping.set_args(['-c', '3', host])
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
    def _ping(options: Options) -> str:
        task = subtask_mod.Batch(options.get_ping().get_cmdline())
        task.run(pattern=options.get_pattern())
        if task.has_output():
            return options.get_host() + ' is alive'
        return options.get_host() + ' is dead'

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        stat = ''
        while options.get_repeat_flag():
            test = self._ping(options)
            if test != stat:
                print(f"{time.strftime('%Y-%m-%d-%H:%M:%S')}: {test}")
                stat = test
            time.sleep(5)
        print(self._ping(options))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
