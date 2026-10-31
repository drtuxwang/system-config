#!/usr/bin/env python3
"""
Desktop audio volume utility.
"""

import argparse
import signal
import sys
from typing import List, Tuple

from command_mod import Command
from subtask_mod import Batch, Task

MAX_VOLUME = 200


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_settings(self) -> Tuple[int, int]:
        """
        Return settings tuple.
        """
        return self._settings

    @staticmethod
    def _getvol() -> int:
        wpctl = Command('wpctl', errors='stop')
        task = Batch(wpctl.get_cmdline() + ['get-volume', '@DEFAULT_SINK@'])
        task.run(pattern='^Volume: ', error2output=True)
        try:
            for line in task.get_output():
                if line.startswith('Volume: '):
                    return int(float(line.split()[-1]) * 100)
        except ValueError:
            pass
        raise SystemExit(
            f'{sys.argv[0]}: Cannot detect current Pipewire volume.',
        )

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

        volume = self._getvol()
        print("debugX1", volume)
        if change == '+':
            new_volume = min(round(int(volume+10.01), -1), MAX_VOLUME)
        elif change == '-':
            new_volume = max(round(int(volume-9.99), -1), 0)
        elif change == '=':
            new_volume = 100
        else:
            new_volume = min(volume, MAX_VOLUME)
        self._settings = (volume, new_volume)


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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        wpctl = Command('wpctl', errors='stop')
        volume, new_volume = options.get_settings()
        print(f"Output : {volume}% => {new_volume}%")
        wpctl.set_args([
            'set-volume',
            '@DEFAULT_AUDIO_SINK@',
            f'{new_volume/100}',
        ])
        Task(wpctl.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
