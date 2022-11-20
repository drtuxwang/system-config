#!/usr/bin/env python3
"""
Desktop audio volume utility.
"""

import argparse
import glob
import os
import signal
import sys
from typing import Generator, List

import command_mod
import subtask_mod

MAX_VOLUME = 200


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_settings(self) -> dict:
        """
        Return settings dictionary.
        """
        return self._settings

    @staticmethod
    def _getvol() -> Generator[tuple, None, None]:
        pacmd = command_mod.Command('pacmd', errors='stop')
        task = subtask_mod.Batch(pacmd.get_cmdline() + ['list-sinks'])
        task.run(pattern='index:|\tvolume:.*%')
        index = '0'
        try:
            for line in task.get_output():
                if 'index:' in line:
                    index = line.split()[-1]
                elif 'volume:' in line:
                    percent = int(line.split('%', 1)[0].split()[-1])
                    yield (index, percent)
        except ValueError as exception:
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
        change = self._args.change

        self._settings = {}
        for index, volume in self._getvol():
            if change == '+':
                new_volume = min(round(int(volume+5.01), -1), MAX_VOLUME)
            elif change == '-':
                new_volume = max(round(int(volume-5.99), -1), 0)
            elif change == '=':
                new_volume = 100
            else:
                new_volume = min(volume, MAX_VOLUME)
            self._settings[index] = (volume, new_volume)


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

        pactl = command_mod.Command('pactl', errors='stop')
        for index, settings in sorted(options.get_settings().items()):
            print(f"Output {index}: {settings[0]}% => {settings[1]}%")
            pactl.set_args(['set-sink-volume', f'{index}', f'{settings[1]}%'])
            subtask_mod.Task(pactl.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
