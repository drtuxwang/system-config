#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import signal
import sys

import power_mod

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")


class Main(object):
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
    def _show(battery):
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

    def run(self):
        """
        Start program
        """
        batteries = power_mod.Battery.factory()

        for battery in batteries:
            if battery.is_exist():
                self._show(battery)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
