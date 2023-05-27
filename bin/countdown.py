#!/usr/bin/env python3
"""
Count down timer.
"""

import argparse
import signal
import sys
import time
from typing import List

import command_mod
import subtask_mod

TEXT_FONT = '*-fixed-bold-*-18-*-iso10646-*'
FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_pop(self) -> command_mod.Command:
        """
        Return pop Command class object.
        """
        return self._pop

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Count down timer.")

        parser.add_argument(
            '-g',
            dest='gui_flag',
            action='store_true',
            help="Start GUI.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.gui_flag:
            xterm = command_mod.Command('xterm', errors='stop')
            xterm.set_args([
                '-fn',
                TEXT_FONT,
                '-fg',
                FG_COLOUR,
                '-bg',
                BG_COLOUR,
                '-cr',
                '#880000',
                '-geometry',
                '15x4+120+20',
                '-ut',
                '+sb',
                '-e',
                sys.argv[0]
            ] + args[2:])
            subtask_mod.Daemon(xterm.get_cmdline()).run()
            raise SystemExit(0)

        self._pop = command_mod.Command('notify-send', errors='stop')
        self._pop.set_args(['--expire-time', '10000'])


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

    def _alert(self) -> None:
        if self._alarm < 61:
            sys.stdout.write("\033]11;#ff8888\007")
            sys.stdout.flush()
            subtask_mod.Batch(self._bell.get_cmdline()).run()
            self._options.get_pop().set_args(
                [time.strftime('%H:%M') + ': Count down reminder']
            )
            subtask_mod.Batch(self._options.get_pop().get_cmdline()).run()
        self._alarm += 60  # One minute reminder

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        self._bell = command_mod.Command('bell', errors='stop')
        self._alarm = None

        while True:
            try:
                sys.stdout.write("\033]11;#ffffdd\007")
                try:
                    count_down = int(input("Time(s): "))
                except ValueError:
                    continue
                elapsed = 0
                self._alarm = 0
                start = int(time.time())

                while True:
                    if elapsed >= count_down + self._alarm:
                        self._alert()
                    time.sleep(1)
                    elapsed = int(time.time()) - start
                    sys.stdout.write(
                        f" \r {time.strftime('%H:%M')} "
                        f"{count_down - elapsed}",
                    )
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
