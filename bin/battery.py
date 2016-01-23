#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import glob
import os
import re
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._batterys = []
        if os.path.isdir('/sys/class/power_supply'):
            for directory in glob.glob('/sys/class/power_supply/BAT*'):  # New kernels
                self._batterys.append(BatteryPower(directory))
        else:
            for directory in glob.glob('/proc/acpi/battery/BAT*'):
                self._batterys.append(BatteryAcpi(directory))
        if not self._batterys:
            raise SystemExit(sys.argv[0] + ': Cannot find any battery device.')

    def get_batteries(self):
        """
        Return list of batterys.
        """
        return self._batterys


class BatteryAcpi(object):
    """
    Uses '/proc/acpi/battery/BAT*'
    """

    def __init__(self, directory):
        self._device = os.path.basename(directory)
        self._oem = 'Unknown'
        self._name = 'Unknown'
        self._type = 'Unknown'
        self._capacity_max = -1
        self._voltage = -1
        self._isjunk = re.compile('^.*: *| .*$')
        self._state = os.path.join(directory, 'state')

        with open(os.path.join(directory, 'info'), errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip()
                if line.startswith('OEM info:'):
                    self._oem = self._isjunk.sub('', line)
                elif line.startswith('model number:'):
                    self._name = self._isjunk.sub('', line)
                elif line.startswith('battery type:'):
                    self._type = self._isjunk.sub('', line)
                elif line.startswith('design capacity:'):
                    try:
                        self._capacity_max = int(self._isjunk.sub('', line))
                    except ValueError:
                        pass
                elif line.startswith('design voltage:'):
                    try:
                        self._voltage = int(self._isjunk.sub('', line))
                    except ValueError:
                        pass
        self.check()

    def check(self):
        self._is_exist = False
        self._capacity = -1
        self._charge = '='
        self._rate = 0

        try:
            with open(self._state, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip()
                    if line.startswith('present:'):
                        if self._isjunk.sub('', line) == 'yes':
                            self._is_exist = True
                    elif line.startswith('charging state:'):
                        state = self._isjunk.sub('', line)
                        if state == 'discharging':
                            self._charge = '-'
                        elif state == 'charging':
                            self._charge = '+'
                    elif line.startswith('present rate:'):
                        try:
                            self._rate = abs(int(self._isjunk.sub('', line)))
                        except ValueError:
                            pass
                    elif line.startswith('remaining capacity:'):
                        try:
                            self._capacity = int(self._isjunk.sub('', line))
                        except ValueError:
                            pass
        except OSError:
            return

    def is_exist(self):
        """
        Return exist flag.
        """
        return self._is_exist

    def get_capacity(self):
        return self._capacity

    def get_capacity_max(self):
        return self._capacity_max

    def get_charge(self):
        return self._charge

    def get_name(self):
        return self._name

    def get_oem(self):
        return self._oem

    def get_rate(self):
        return self._rate

    def get_type(self):
        return self._type

    def get_voltage(self):
        return self._voltage


class BatteryPower(BatteryAcpi):
    """
    Uses '/sys/class/power_supply/BAT*'
    """

    def __init__(self, directory):
        self._device = os.path.basename(directory)
        self._oem = 'Unknown'
        self._name = 'Unknown'
        self._type = 'Unknown'
        self._capacity_max = -1
        self._voltage = -1
        self._isjunk = re.compile('^[^=]*=| .*$')
        self._state = os.path.join(directory, 'uevent')

        with open(self._state, errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip()
                if '_MANUFACTURER=' in line:
                    self._oem = self._isjunk.sub('', line)
                elif '_MODEL_NAME=' in line:
                    self._name = self._isjunk.sub('', line)
                elif '_TECHNOLOGY=' in line:
                    self._type = self._isjunk.sub('', line)
                elif '_CHARGE_FULL_DESIGN=' in line:
                    try:
                        self._capacity_max = int(int(self._isjunk.sub('', line)) / 1000)
                    except ValueError:
                        pass
                elif '_ENERGY_FULL_DESIGN=' in line:
                    try:
                        self._capacity_max = int(int(self._isjunk.sub('', line)) / self._voltage)
                    except ValueError:
                        pass
                elif '_VOLTAGE_MIN_DESIGN=' in line:
                    try:
                        self._voltage = int(int(self._isjunk.sub('', line)) / 1000)
                    except ValueError:
                        pass
        self.check()

    def check(self):
        self._is_exist = False
        self._capacity = -1
        self._charge = '='
        self._rate = 0

        try:
            with open(self._state, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip()
                    if '_PRESENT=' in line:
                        if self._isjunk.sub('', line) == '1':
                            self._is_exist = True
                    elif '_STATUS=' in line:
                        state = self._isjunk.sub('', line)
                        if state == 'Discharging':
                            self._charge = '-'
                        elif state == 'Charging':
                            self._charge = '+'
                    elif '_CURRENT_NOW=' in line:
                        try:
                            self._rate = abs(int(int(self._isjunk.sub('', line)) / 1000))
                        except ValueError:
                            pass
                    elif '_POWER_NOW=' in line:
                        try:
                            self._rate = abs(int(int(self._isjunk.sub('', line)) / self._voltage))
                        except ValueError:
                            pass
                    elif '_CHARGE_NOW=' in line:
                        try:
                            self._capacity = int(int(self._isjunk.sub('', line)) / 1000)
                        except ValueError:
                            pass
                    elif '_ENERGY_NOW=' in line:
                        try:
                            self._capacity = int(int(self._isjunk.sub('', line)) / self._voltage)
                        except ValueError:
                            pass
        except OSError:
            return


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
            options = Options(sys.argv)
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
