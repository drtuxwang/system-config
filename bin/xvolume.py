#!/usr/bin/env python3
"""
Desktop audio volume utility.
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

    def get_pacmd(self) -> command_mod.Command:
        """
        Return pacmd Command class object.
        """
        return self._pacmd

    def _getvol(self) -> int:
        self._pacmd.set_args(['dump'])
        task = subtask_mod.Batch(self._pacmd.get_cmdline())
        task.run(pattern='^set-sink-volume')
        try:
            # From 0 - 15
            return int(int(task.get_output()[0].split()[2], 16) / 0x1000)
        except (IndexError, ValueError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot detect current Pulseaudio volume.',
            ) from exception

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Desktop audio volume utility.",
        )

        parser.add_argument(
            '-dec',
            action='store_const',
            const='-',
            dest='change',
            help="Increase brightness.",
        )
        parser.add_argument(
            '-inc',
            action='store_const',
            const='+',
            dest='change',
            help="Default brightness.",
        )
        parser.add_argument(
            '-reset',
            action='store_const',
            const='=',
            dest='change',
            help="Decrease brightness.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._pacmd = command_mod.Command('pacmd', errors='stop')

        change = self._args.change
        if change == '+':
            volume = min(self._getvol() + 1, 16)
        elif change == '-':
            volume = max(self._getvol() - 1, 0)
        elif change == '=':
            volume = 10
        else:
            volume = self._getvol()
        self._pacmd.set_args(['set-sink-volume', '0', f'0x{volume*0x10000:X}'])


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

        subtask_mod.Exec(options.get_pacmd().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
