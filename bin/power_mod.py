#!/usr/bin/env python3
"""
Python power handling module

Copyright GPL v2: 2011-2019 By Dr Colin Kong
"""

import functools
import glob
import os
import re
import subprocess
import sys

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '2.1.9'
VERSION = 20190602


class Battery:
    """
    Battery base class
    """

    def __init__(self, directory):
        self._info = {
            'oem_name': 'Unknown',
            'model_name': 'Unknown',
            'type': 'Unknown',
            'capacity_max': -1,
            'voltage': -1
        }
        self._state = None
        self._isjunk = None
        self._config(directory)
        self.check()

    @staticmethod
    def factory():
        """
        Return list of Battery sub class objects
        """
        devices = []

        if os.path.isdir('/sys/class/power_supply'):  # New kernels
            for directory in glob.glob('/sys/class/power_supply/BAT*'):
                devices.append(BatteryPower(directory))
        elif os.path.isdir('/proc/acpi/battery'):
            for directory in glob.glob('/proc/acpi/battery/BAT*'):
                devices.append(BatteryAcpi(directory))
        elif _System.is_mac():
            if os.path.isfile('/usr/sbin/ioreg'):
                devices = BatteryMac.factory()

        return devices

    def _config(self, _):
        self._is_exist = False

    def is_exist(self):
        """
        Return exist flag.
        """
        return self._is_exist

    def get_capacity(self):
        """
        Return current capcity
        """
        return self._info['capacity']

    def get_capacity_max(self):
        """
        Return max capcity
        """
        return self._info['capacity_max']

    def get_charge(self):
        """
        Return charge change mode
        """
        return self._info['charge']

    def get_name(self):
        """
        Return model name
        """
        return self._info['model_name']

    def get_oem(self):
        """
        Return OEM name
        """
        return self._info['oem_name']

    def get_rate(self):
        """
        Return chargee change rate
        """
        return self._info['rate']

    def get_type(self):
        """
        Return battery type
        """
        return self._info['type']

    def get_voltage(self):
        """
        Return voltage
        """
        return self._info['voltage']

    def check(self):
        """
        Check status
        """


class BatteryAcpi(Battery):
    """
    Battery ACPI class

    Uses old '/proc/acpi/battery/BAT*' interface
    """

    def _config(self, directory):
        self._state = os.path.join(directory, 'state')
        self._isjunk = re.compile('^.*: *| .*$')
        with open(os.path.join(
                directory,
                'info'
        ), errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip()
                if line.startswith('OEM info:'):
                    self._info['oem_name'] = self._isjunk.sub('', line)
                elif line.startswith('model number:'):
                    self._info['model_name'] = self._isjunk.sub('', line)
                elif line.startswith('battery type:'):
                    self._info['type'] = self._isjunk.sub('', line)
                elif line.startswith('design capacity:'):
                    try:
                        self._info['capacity_max'] = int(
                            self._isjunk.sub('', line))
                    except ValueError:
                        pass
                elif line.startswith('design voltage:'):
                    try:
                        self._info['voltage'] = int(
                            self._isjunk.sub('', line))
                    except ValueError:
                        pass
        self.check()

    def check(self):
        """
        Check status
        """
        self._is_exist = False
        self._info['capacity'] = -1
        self._info['charge'] = '='
        self._info['rate'] = 0

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
                            self._info['charge'] = '-'
                        elif state == 'charging':
                            self._info['charge'] = '+'
                    elif line.startswith('present rate:'):
                        try:
                            self._info['rate'] = abs(
                                int(self._isjunk.sub('', line)))
                        except ValueError:
                            pass
                    elif line.startswith('remaining capacity:'):
                        try:
                            self._info['capacity'] = int(
                                self._isjunk.sub('', line))
                        except ValueError:
                            pass
        except OSError:
            return


class BatteryPower(Battery):
    """
    Battery Power class

    Uses new '/sys/class/power_supply/BAT*' interface
    """

    def _config(self, directory):
        self._state = os.path.join(directory, 'uevent')
        self._isjunk = re.compile('^[^=]*=| .*$')
        with open(self._state, errors='replace') as ifile:
            self._state = os.path.join(directory, 'uevent')
            for line in ifile:
                line = line.rstrip()
                try:
                    if '_MANUFACTURER=' in line:
                        self._info['oem_name'] = self._isjunk.sub('', line)
                    elif '_MODEL_NAME=' in line:
                        self._info['model_name'] = self._isjunk.sub('', line)
                    elif '_TECHNOLOGY=' in line:
                        self._info['type'] = self._isjunk.sub('', line)
                    elif '_CHARGE_FULL_DESIGN=' in line:
                        self._info['capacity_max'] = int(
                            int(self._isjunk.sub('', line)) / 1000)
                    elif '_ENERGY_FULL_DESIGN=' in line:
                        self._info['capacity_max'] = int(
                            int(self._isjunk.sub('', line)) /
                            self._info['voltage']
                        )
                    elif '_VOLTAGE_MIN_DESIGN=' in line:
                        self._info['voltage'] = int(
                            int(self._isjunk.sub('', line)) / 1000)
                except ValueError:
                    pass

    def check(self):
        """
        Check status
        """
        self._is_exist = False
        self._info['capacity'] = -1
        self._info['charge'] = '='
        self._info['rate'] = 0

        try:
            with open(self._state, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip()
                    try:
                        if '_PRESENT=' in line:
                            if self._isjunk.sub('', line) == '1':
                                self._is_exist = True
                        elif '_STATUS=' in line:
                            state = self._isjunk.sub('', line)
                            if state == 'Discharging':
                                self._info['charge'] = '-'
                            elif state == 'Charging':
                                self._info['charge'] = '+'
                        elif '_CURRENT_NOW=' in line:
                            self._info['rate'] = abs(
                                int(int(self._isjunk.sub('', line)) / 1000))
                        elif '_POWER_NOW=' in line:
                            self._info['rate'] = abs(int(
                                int(self._isjunk.sub('', line)) /
                                self._info['voltage']
                            ))
                        elif '_CHARGE_NOW=' in line:
                            self._info['capacity'] = int(
                                int(self._isjunk.sub('', line)) /
                                1000
                            )
                        elif '_ENERGY_NOW=' in line:
                            self._info['capacity'] = int(
                                int(self._isjunk.sub('', line)) /
                                self._info['voltage']
                            )
                    except ValueError:
                        pass
        except OSError:
            return


class BatteryMac(Battery):
    """
    Battery Mac class

    Uses '/usr/sbin/ioreg' utility
    """

    @staticmethod
    def factory():
        devices = []

        data = {}
        for line in _System.run_program(['/usr/sbin/ioreg', '-l']):
            if "Battery  <" in line:
                data['id'] = line.split('id ')[1].split(',')[0]
                data['type'] = line.split('class ')[1].split(',')[0]
            elif data:
                if '"' in line:
                    key, value = line.split(
                        '"', 1)[1].replace('"', '').split(' = ')
                    data[key] = value
                elif '}' in line and 'id' in data:
                    devices.append(BatteryMac(data))
                    data = {}

        return devices

    def _config(self, data):
        try:
            self._info['id'] = data['id']
            self._info['capacity_max'] = data['DesignCapacity']
            self._info['model_name'] = data['BatterySerialNumber']
            self._info['oem_name'] = data.get(
                'Manufacturer',
                data['DeviceName'],
            )
            self._info['type'] = data['type']
        except ValueError:
            pass

    def check(self):
        data = {}
        for line in _System.run_program(['/usr/sbin/ioreg', '-l']):
            if "Battery  <" in line and self._info['id'] in line:
                data['id'] = line.split('id ')[1].split(',')[0]
                data['type'] = line.split('class ')[1].split(',')[0]
            elif data:
                if '"' in line:
                    key, value = line.split(
                        '"', 1)[1].replace('"', '').split(' = ')
                    data[key] = value
                elif '}' in line and 'id' in data:
                    break

        try:
            self._is_exist = data['BatteryInstalled'] == 'Yes'
            self._info['capacity'] = data['CurrentCapacity']
            self._info['voltage'] = int(data['Voltage'])
            hours = int(data['TimeRemaining']) / 60
            if hours == 0:
                self._info['charge'] = '='
            elif data['IsCharging'] == 'Yes':
                self._info['charge'] = '+'
                self._info['rate'] = int(
                    int(data['MaxCapacity']) -
                    int(self._info['capacity']) /
                    hours
                )
            else:
                self._info['charge'] = '-'
                self._info['rate'] = int(int(self._info['capacity']) / hours)
        except ValueError:
            pass


class _System:

    @staticmethod
    def is_mac():
        """
        Return True if running on MacOS.
        """
        if os.name == 'posix' and os.uname()[0].startswith('Darwin'):
            return True
        return False

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _locate_program(program):
        for directory in os.environ['PATH'].split(os.pathsep):
            file = os.path.join(directory, program)
            if os.path.isfile(file):
                break
        else:
            raise CommandNotFoundError(
                'Cannot find required "' + program + '" software.'
            )
        return file

    @classmethod
    def run_program(cls, command):
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        try:
            child = subprocess.Popen(
                [program] + command[1:],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + program + '" program.'
            )
        lines = []
        while True:
            try:
                line = child.stdout.readline().decode('utf-8', 'replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            lines.append(line.rstrip('\r\n'))
        return lines


class PowerError(Exception):
    """
    Power module error.
    """


class CommandNotFoundError(PowerError):
    """
    Command not found error.
    """


class ExecutableCallError(PowerError):
    """
    Executable call error.
    """


if __name__ == '__main__':
    help(__name__)
