#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import argparse
import signal
import sys

import power_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_summary_flag(self):
        """
        Return summary flag.
        """
        return self._args.summary_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Monitor laptop battery.')

        parser.add_argument(
            '-s',
            action='store_true',
            dest='summary_flag',
            help='Show summary'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def _show_battery(battery):
        model = (
            battery.get_oem() + ' ' + battery.get_name() + ' ' +
            battery.get_type() + ' ' + str(battery.get_capacity_max()) +
            'mAh/' + str(battery.get_voltage()) + 'mV'
        )
        if battery.get_charge() == '-':
            state = '-'
            if battery.get_rate() > 0:
                state += str(battery.get_rate()) + 'mA'
                if battery.get_voltage() > 0:
                    power = '{0:4.2f}'.format(float(
                        battery.get_rate()*battery.get_voltage()) / 1000000)
                    state += ', ' + str(power) + 'W'
                hours = '{0:3.1f}'.format(float(
                    battery.get_capacity()) / battery.get_rate())
                state += ', ' + str(hours) + 'h'
        elif battery.get_charge() == '+':
            state = '+'
            if battery.get_rate() > 0:
                state += str(battery.get_rate()) + 'mA'
                if battery.get_voltage() > 0:
                    power = '{0:4.2f}'.format(float(
                        battery.get_rate()*battery.get_voltage()) / 1000000)
                    state += ', ' + str(power) + 'W'
        else:
            state = 'Unused'
        print(
            model + " = ", battery.get_capacity(),
            "mAh [" + state + "]",
            sep=""
        )

    @staticmethod
    def _show_summary(batteries):
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
                print("{0:d}mAh [{1:+d}mAh]".format(capacity, rate))
            else:
                print("{0:d}mAh [Unused]".format(capacity))

    def run(self):
        """
        Start program
        """
        options = Options()
        batteries = power_mod.Battery.factory()

        if options.get_summary_flag():
            self._show_summary(batteries)
        else:
            for battery in batteries:
                if battery.is_exist():
                    self._show_battery(battery)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
