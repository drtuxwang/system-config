#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import argparse
import signal
import sys
from typing import List

from power_mod import Battery


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_summary_flag(self) -> bool:
        """
        Return summary flag.
        """
        return self._args.summary_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Monitor laptop battery.",
        )

        parser.add_argument(
            '-s',
            action='store_true',
            dest='summary_flag',
            help="Show summary"
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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def _show_battery(battery: Battery) -> None:
        model = (
            f'{battery.get_oem()} {battery.get_name()} {battery.get_type()} '
            f'{battery.get_capacity_max()}mAh/{battery.get_voltage()}mV'
        )
        if battery.get_charge() == '-':
            state = '-'
            if battery.get_rate() > 0:
                state += str(battery.get_rate()) + 'mA'
                if battery.get_voltage() > 0:
                    power = battery.get_rate() * battery.get_voltage()
                    state += f', {power / 1000000:4.2f}W'
                hours = battery.get_capacity() / battery.get_rate()
                state += f', {hours:3.1f}h'
        elif battery.get_charge() == '+':
            state = '+'
            if battery.get_rate() > 0:
                state += str(battery.get_rate()) + 'mA'
                if battery.get_voltage() > 0:
                    power = battery.get_rate() * battery.get_voltage()
                    state += f', {power / 1000000:4.2f}W'
        else:
            state = 'Unused'

        # Add battery percent and threshold
        start, stop = battery.get_thresholds()
        if stop >= 0:
            state = f"{start}-{stop}%, {state}"
        percent = battery.get_capacity_percent()
        if percent:
            state = f"{percent}%, {state}"

        print(f"{model} = {battery.get_capacity()}mAh [{state}]", sep="")

    @staticmethod
    def _show_summary(batteries: List[Battery]) -> None:
        capacity = 0
        rate = 0
        for battery in batteries:
            if battery.is_exist():
                capacity += battery.get_capacity()
                if battery.get_charge() == '-':
                    rate -= battery.get_rate()
                elif battery.get_charge() == '+':
                    rate += battery.get_rate()

        if capacity:
            if rate:
                print(f"{capacity:d}mAh [{rate:+d}mAh]")
            else:
                print(f"{capacity:d}mAh [Unused]")

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        batteries = Battery.factory()

        if options.get_summary_flag():
            self._show_summary(batteries)
        else:
            for battery in batteries:
                if battery.is_exist():
                    self._show_battery(battery)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
