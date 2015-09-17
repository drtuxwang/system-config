#!/usr/bin/env python3
"""
Monitor laptop battery
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._batterys = []
        if os.path.isdir("/sys/class/power_supply"):
            for directory in glob.glob("/sys/class/power_supply/BAT*"): # New kernels
                self._batterys.append(BatteryPower(directory))
        else:
            for directory in glob.glob("/proc/acpi/battery/BAT*"):
                self._batterys.append(BatteryAcpi(directory))
        if not self._batterys:
            raise SystemExit(sys.argv[0] + ": Cannot find any battery device.")


    def getBatterys(self):
        """
        Return list of batterys.
        """
        return self._batterys


class BatteryAcpi(syslib.Dump):
    """
    Uses "/proc/acpi/battery/BAT*"
    """


    def __init__(self, directory):
        self._device = os.path.basename(directory)
        self._oem = "Unknown"
        self._name = "Unknown"
        self._type = "Unknown"
        self._capacityMax = -1
        self._voltage = -1
        self._isjunk = re.compile("^.*: *| .*$")
        self._state = os.path.join(directory, "state")

        with open(os.path.join(directory, "info"), errors="replace") as ifile:
            for line in ifile:
                line = line.rstrip()
                if line.startswith("OEM info:"):
                    self._oem = self._isjunk.sub("", line)
                elif line.startswith("model number:"):
                    self._name = self._isjunk.sub("", line)
                elif line.startswith("battery type:"):
                    self._type = self._isjunk.sub("", line)
                elif line.startswith("design capacity:"):
                    try:
                        self._capacityMax = int(self._isjunk.sub("", line))
                    except ValueError:
                        pass
                elif line.startswith("design voltage:"):
                    try:
                        self._voltage = int(self._isjunk.sub("", line))
                    except ValueError:
                        pass
        self.check()


    def check(self):
        self._isExist = False
        self._capacity = -1
        self._charge = "="
        self._rate = 0

        try:
            with open(self._state, errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip()
                    if line.startswith("present:"):
                        if self._isjunk.sub("", line) == "yes":
                            self._isExist = True
                    elif line.startswith("charging state:"):
                        state = self._isjunk.sub("", line)
                        if state == "discharging":
                            self._charge = "-"
                        elif state == "charging":
                            self._charge = "+"
                    elif line.startswith("present rate:"):
                        try:
                            self._rate = abs(int(self._isjunk.sub("", line)))
                        except ValueError:
                            pass
                    elif line.startswith("remaining capacity:"):
                        try:
                            self._capacity = int(self._isjunk.sub("", line))
                        except ValueError:
                            pass
        except IOError:
            return


    def isExist(self):
        """
        Return exist flag.
        """
        return self._isExist


    def getCapacity(self):
        return self._capacity


    def getCapacityMax(self):
        return self._capacityMax


    def getCharge(self):
        return self._charge


    def getName(self):
        return self._name


    def getOem(self):
        return self._oem


    def getRate(self):
        return self._rate


    def getType(self):
        return self._type


    def getVoltage(self):
        return self._voltage


class BatteryPower(BatteryAcpi):
    """
    Uses "/sys/class/power_supply/BAT*"
    """


    def __init__(self, directory):
        self._device = os.path.basename(directory)
        self._oem = "Unknown"
        self._name = "Unknown"
        self._type = "Unknown"
        self._capacityMax = -1
        self._voltage = -1
        self._isjunk = re.compile("^[^=]*=| .*$")
        self._state = os.path.join(directory, "uevent")

        with open(self._state, errors="replace") as ifile:
            for line in ifile:
                line = line.rstrip()
                if "_MANUFACTURER=" in line:
                    self._oem = self._isjunk.sub("", line)
                elif "_MODEL_NAME=" in line:
                    self._name = self._isjunk.sub("", line)
                elif "_TECHNOLOGY=" in line:
                    self._type = self._isjunk.sub("", line)
                elif "_CHARGE_FULL_DESIGN=" in line:
                    try:
                        self._capacityMax = int(int(self._isjunk.sub("", line)) / 1000)
                    except ValueError:
                        pass
                elif "_ENERGY_FULL_DESIGN=" in line:
                    try:
                        self._capacityMax = int(int(self._isjunk.sub("", line)) / self._voltage)
                    except ValueError:
                        pass
                elif "_VOLTAGE_MIN_DESIGN=" in line:
                    try:
                        self._voltage = int(int(self._isjunk.sub("", line)) / 1000)
                    except ValueError:
                        pass
        self.check()


    def check(self):
        self._isExist = False
        self._capacity = -1
        self._charge = "="
        self._rate = 0

        try:
            with open(self._state, errors="replace") as ifile:
                for line in ifile:
                    line = line.rstrip()
                    if "_PRESENT=" in line:
                        if self._isjunk.sub("", line) == "1":
                            self._isExist = True
                    elif "_STATUS=" in line:
                        state = self._isjunk.sub("", line)
                        if state == "Discharging":
                            self._charge = "-"
                        elif state == "Charging":
                            self._charge = "+"
                    elif "_CURRENT_NOW=" in line:
                        try:
                            self._rate = abs(int(int(self._isjunk.sub("", line)) / 1000))
                        except ValueError:
                            pass
                    elif "_POWER_NOW=" in line:
                        try:
                            self._rate = abs(int(int(self._isjunk.sub("", line)) / self._voltage))
                        except ValueError:
                            pass
                    elif "_CHARGE_NOW=" in line:
                        try:
                            self._capacity = int(int(self._isjunk.sub("", line)) / 1000)
                        except ValueError:
                            pass
                    elif "_ENERGY_NOW=" in line:
                        try:
                            self._capacity = int(int(self._isjunk.sub("", line)) / self._voltage)
                        except ValueError:
                            pass
        except IOError:
            return


class Monitor(syslib.Dump):


    def __init__(self, options):
        for battery in options.getBatterys():
            if battery.isExist():
                self._show(battery)


    def _show(self, battery):
        model = (battery.getOem() + " " + battery.getName() + " " + battery.getType() + " " +
                 str(battery.getCapacityMax()) + "mAh/" + str(battery.getVoltage()) + "mV")
        if battery.getCharge() == "-":
            state="-"
            if battery.getRate() > 0:
                state += str(battery.getRate()) + "mA"
                if battery.getVoltage() > 0:
                    power = "{0:4.2f}".format(float(
                            battery.getRate()*battery.getVoltage()) / 1000000)
                    state += ", " + str(power) + "W"
                hours = "{0:3.1f}".format(float(
                        battery.getCapacity()) / battery.getRate())
                state += ", " + str(hours) + "h"
        elif battery.getCharge() == "+":
            state = "+"
            if battery.getRate() > 0:
                state += str(battery.getRate()) + "mA"
                if battery.getVoltage() > 0:
                    power = "{0:4.2f}".format(float(
                            battery.getRate()*battery.getVoltage()) / 1000000)
                    state += ", " + str(power) + "W"
        else:
            state = "Unused"
        print(model + " = ", battery.getCapacity(), "mAh [" + state + "]", sep="")


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Monitor(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
