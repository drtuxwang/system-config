#!/usr/bin/env python3
"""
Python power handling module

Copyright GPL v2: 2011-2022 By Dr Colin Kong
"""

import functools
import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

RELEASE = '2.4.0'
VERSION = 20221218


class Battery:
    """
    Battery base class
    """

    def __init__(self, path: Path = None) -> None:
        self._path = path
        self._info: dict = {
            'oem_name': 'Unknown',
            'model_name': 'Unknown',
            'type': 'Unknown',
            'capacity_max': -1,
            'charge_max': -1,
            'voltage': -1,
            'thresholds': (0, -1),
        }
        self._isjunk = re.compile('')
        self._config()
        self.check()

    @staticmethod
    def factory() -> List['Battery']:
        """
        Return list of Battery sub class objects
        """
        devices: List[Battery] = []

        if Path('/sys/class/power_supply').is_dir():  # New kernels
            for path in Path('/sys/class/power_supply').glob('BAT*'):
                devices.append(BatteryPower(path))
        elif Path('/proc/acpi/battery').is_dir():
            for path in Path('/proc/acpi/battery').glob('BAT*'):
                devices.append(BatteryAcpi(path))
        elif _System.is_mac():
            if Path('/usr/sbin/ioreg').is_file():
                devices = BatteryMac.factory()

        return devices

    @staticmethod
    def _read_file(path: Path) -> List[str]:
        lines = []
        try:
            with path.open(encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except OSError:
            lines = []
        return lines

    def _config(self) -> None:
        self._is_exist = False

    def is_exist(self) -> bool:
        """
        Return exist flag.
        """
        return self._is_exist

    def get_capacity(self) -> int:
        """
        Return current capacity
        """
        return self._info['capacity']

    def get_capacity_percent(self) -> str:
        """
        Return charge percentage of max charge
        """
        percent = int(self._info['capacity'] / self._info['charge_max'] * 100)
        if percent >= 0:
            return f"{percent}"
        return ""

    def get_capacity_max(self) -> int:
        """
        Return max design capcity
        """
        return self._info['capacity_max']

    def get_charge(self) -> str:
        """
        Return current charge
        """
        return self._info['charge']

    def get_name(self) -> str:
        """
        Return model name
        """
        return self._info['model_name']

    def get_oem(self) -> str:
        """
        Return OEM name
        """
        return self._info['oem_name']

    def get_rate(self) -> int:
        """
        Return charge change rate
        """
        return self._info['rate']

    def get_thresholds(self) -> Tuple[int, int]:
        """
        Return tuple of charge thresholds
        """
        return self._info['thresholds']

    def get_type(self) -> str:
        """
        Return battery type
        """
        return self._info['type']

    def get_voltage(self) -> int:
        """
        Return voltage
        """
        return self._info['voltage']

    def check(self) -> None:
        """
        Check status
        """


class BatteryAcpi(Battery):
    """
    Battery ACPI class

    Uses old '/proc/acpi/battery/BAT*' interface
    """

    def _config(self) -> None:
        self._isjunk = re.compile('^.*: *| .*$')
        for line in self._read_file(Path(self._path, 'info')):
            try:
                if line.startswith('OEM info:'):
                    self._info['oem_name'] = self._isjunk.sub('', line)
                elif line.startswith('model number:'):
                    self._info['model_name'] = self._isjunk.sub('', line)
                elif line.startswith('battery type:'):
                    self._info['type'] = self._isjunk.sub('', line)
                elif line.startswith('design capacity:'):
                    self._info['capacity_max'] = int(
                        self._isjunk.sub('', line)
                    )
                elif line.startswith('design voltage:'):
                    self._info['voltage'] = int(self._isjunk.sub('', line))
            except ValueError:
                pass
        self.check()

    def check(self) -> None:
        """
        Check status
        """
        self._is_exist = False
        self._info['capacity'] = -1
        self._info['charge'] = '='
        self._info['rate'] = 0

        for line in self._read_file(Path(self._path, 'state')):
            try:
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
                    self._info['rate'] = abs(int(self._isjunk.sub('', line)))
                elif line.startswith('remaining capacity:'):
                    self._info['capacity'] = int(self._isjunk.sub('', line))
            except ValueError:
                pass


class BatteryPower(Battery):
    """
    Battery Power class

    Uses new '/sys/class/power_supply/BAT*' interface
    """

    def _config(self) -> None:
        self._isjunk = re.compile('^[^=]*=| .*$')
        for line in self._read_file(Path(self._path, 'uevent')):
            try:
                if '_MANUFACTURER=' in line:
                    self._info['oem_name'] = self._isjunk.sub('', line)
                elif '_MODEL_NAME=' in line:
                    self._info['model_name'] = self._isjunk.sub('', line)
                elif '_TECHNOLOGY=' in line:
                    self._info['type'] = self._isjunk.sub('', line)
                elif '_CHARGE_FULL_DESIGN=' in line:
                    self._info['capacity_max'] = int(
                        int(self._isjunk.sub('', line)) / 1000
                    )
                elif '_ENERGY_FULL_DESIGN=' in line:
                    self._info['capacity_max'] = int(
                        int(self._isjunk.sub('', line)) / self._info['voltage']
                    )
                elif '_CHARGE_FULL=' in line:
                    self._info['charge_max'] = int(
                        int(self._isjunk.sub('', line)) / 1000
                    )
                elif '_ENERGY_FULL=' in line:
                    self._info['charge_max'] = int(
                        int(self._isjunk.sub('', line)) / self._info['voltage']
                    )
                elif '_VOLTAGE_MIN_DESIGN=' in line:
                    self._info['voltage'] = int(
                        int(self._isjunk.sub('', line)) / 1000
                    )
            except ValueError:
                pass

    def _get_threshold(self) -> Tuple[int, int]:
        start = '0'
        stop = '-1'

        # Standard (Lenovo ThinkPads) start threshold
        value = ' '.join(self._read_file(
            Path(self._path, 'charge_control_start_threshold'))
        )
        if value:
            start = value
        # Standard (Asus, Lenovo ThinkPads) stop threshold
        value = ' '.join(self._read_file(
            Path(self._path, 'charge_control_end_threshold'))
        )
        if value:
            stop = value

        # IBM legacy ThinkPads start/stop thresholds
        device = Path(self._path).name
        value = ' '.join(self._read_file(Path(
            '/sys/devices/platform/smapi',
            device,
            'start_charge_thresh',
        )))
        if value:
            start = value
        value = ' '.join(self._read_file(Path(
            '/sys/devices/platform/smapi',
            device,
            'stop_charge_thresh',
        )))
        if value:
            stop = value

        # Huawei start/stop thresholds
        values = ' '.join(self._read_file(Path(
            '/sys/devices/platform/huawei-wmi/charge_control_thresholds',
        )))
        if values and ' ' in values:
            start, stop = values.split()

        # Lenovo non-ThinkPad stop threshold
        value = ' '.join(self._read_file(Path(
            '/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00',
            'conservation_mode'
        )))
        if value == '1':
            stop = '60'

        # LG stop threshold
        value = ' '.join(self._read_file(Path(
            '/sys/devices/platform/lg-laptop/battery_care_limit'
        )))
        if value:
            stop = value

        # Samsung stop threshold activated
        value = ' '.join(self._read_file(Path(
            '/sys/devices/platform/samsung/battery_life_extender'
        )))
        if value == '1':
            stop = '80'

        # Sony stop threshold
        value = ' '.join(self._read_file(Path(
            '/sys/devices/platform/sony-laptop/battery_care_limiter'
        )))
        if value:
            stop = value

        try:
            return (int(start), int(stop))
        except ValueError:
            return (0, -1)

    def check(self) -> None:
        """
        Check status
        """
        self._is_exist = False
        self._info['capacity'] = -1
        self._info['charge'] = '='
        self._info['rate'] = 0

        for line in self._read_file(Path(self._path, 'uevent')):
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
                    self._info['rate'] = abs(int(
                        int(self._isjunk.sub('', line)) / 1000
                    ))
                elif '_POWER_NOW=' in line:
                    self._info['rate'] = abs(int(
                        int(self._isjunk.sub('', line)) / self._info['voltage']
                    ))
                elif '_CHARGE_NOW=' in line:
                    self._info['capacity'] = int(
                        int(self._isjunk.sub('', line)) / 1000
                    )
                elif '_ENERGY_NOW=' in line:
                    self._info['capacity'] = int(
                        int(self._isjunk.sub('', line)) / self._info['voltage']
                    )
            except ValueError:
                pass

        self._info['thresholds'] = self._get_threshold()


class BatteryMac(Battery):
    """
    Battery Mac class

    Uses '/usr/sbin/ioreg' utility
    """

    def __init__(self, data: dict) -> None:
        self._data = data
        super().__init__()

    @staticmethod
    def factory() -> List[Battery]:
        devices: List[Battery] = []

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

    def _config(self) -> None:
        try:
            self._info['id'] = self._data['id']
            self._info['capacity_max'] = self._data['DesignCapacity']
            self._info['model_name'] = self._data.get(
                'BatterySerialNumber',
                self._data['Serial'],
            )
            self._info['oem_name'] = self._data.get(
                'Manufacturer',
                self._data['DeviceName'],
            )
            self._info['type'] = self._data['type']
        except ValueError:
            pass

    def check(self) -> None:
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
            self._info['capacity'] = int(data['CurrentCapacity'])
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
    def is_mac() -> bool:
        """
        Return True if running on MacOS.
        """
        if os.name == 'posix' and os.uname()[0].startswith('Darwin'):
            return True
        return False

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _locate_program(program: str) -> Path:
        for directory in os.environ['PATH'].split(os.pathsep):
            path = Path(directory, program)
            if path.is_file():
                break
        else:
            raise CommandNotFoundError(
                f'Cannot find required "{program}" software.',
            )
        return path

    @classmethod
    def run_program(cls, command: List[str]) -> List[str]:
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        lines = []
        try:
            with subprocess.Popen(
                [str(program)] + command[1:],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as child:
                while True:
                    try:
                        bline = child.stdout.readline()
                    except (KeyboardInterrupt, OSError):
                        break
                    if not bline:
                        break
                    line = bline.decode('utf-8', 'replace')
                    lines.append(line.rstrip('\r\n'))
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{program}" program.',
            ) from exception

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
