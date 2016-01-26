#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import glob
import os
import signal
import sys

import ck_battery
import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._batteries = ck_battery.BatteryFactory().detect()
        if not self._batteries:
            raise SystemExit(sys.argv[0] + ': Cannot find any battery device.')

    def get_batteries(self):
        """
        Return list of batteries.
        """
        return self._batteries


class Monitor(object):
    """
    Monitor class
    """

    def __init__(self, options):
        for battery in options.get_batteries():
            if battery.is_exist():
                self._show(battery)

    def _show(self, battery):
        model = (battery.get_oem() + ' ' + battery.get_name() + ' ' + battery.get_type() + ' ' +
                 str(battery.get_capacity_max()) + 'mAh/' + str(battery.get_voltage()) + 'mV')
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
        print(model + ' = ', battery.get_capacity(), 'mAh [' + state + ']', sep='')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options()
            Monitor(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
