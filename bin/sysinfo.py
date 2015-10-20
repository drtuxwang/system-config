#!/usr/bin/env python3
"""
System configuration detection tool.

1996-2015 By Dr Colin Kong
"""

RELEASE = "4.4.4"
VERSION = 20151020

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import math
import os
import re
import signal
import socket
import threading
import time
if os.name == "nt":
    import winreg

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._releaseDate = str(VERSION)[:4] + "-" + str(VERSION)[4:6] + "-" + str(VERSION)[6:]
        self._releaseVersion = RELEASE

        self._system = self._getSystem()

    def getReleaseDate(self):
        """
        Return release date.
        """
        return self._releaseDate

    def getReleaseVersion(self):
        """
        Return release version.
        """
        return self._releaseVersion

    def getSystem(self):
        """
        Return operating syslib.
        """
        return self._system

    def _getSystem(self):
        name = syslib.info.getSystem()
        if name == "linux":
            return LinuxSystem()
        elif name == "windows":
            return WindowsSystem()
        else:
            return OperatingSystem()


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


class CommandThread(syslib.Dump, threading.Thread):

    def __init__(self, command):
        threading.Thread.__init__(self)
        self._child = None
        self._command = command
        self._stdout = ""

    def run(self):
        self._child = self._command.run(mode="child")
        while True:
            try:
                byte = self._child.stdout.read(1)
            except AttributeError:
                continue
            if not byte:
                break
            self._stdout += byte.decode("utf-8", "replace")

    def kill(self):
        if self._child:
            self._child.kill()
            self._child = None

    def getOutput(self):
        """
        Return thread output.
        """
        return self._stdout


class Detect(syslib.Dump):

    def __init__(self, options):
        self._author = ("Sysinfo " + options.getReleaseVersion() +
                        " (" + options.getReleaseDate() + ")")

        self._system = options.getSystem()
        self._writer = Writer(options)

    def run(self):
        timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
        print("\n" + self._author, "- System configuration detection tool")

        print("\n*** Detected at", timestamp, "***")
        self._networkInformation()
        self._operatingSystem()
        self._processors()
        self._systemStatus()
        if self._system.hasDevices():
            self._system.detectDevices(self._writer)
        if self._system.hasLoader():
            self._system.detectLoader(self._writer)
        self._xwindows()
        print()

    def _networkInformation(self):
        info = self._system.getNetInfo()
        self._writer.output(name="Hostname", value=syslib.info.getHostname())
        self._writer.output(name="Net FQDN", value=info["Net FQDN"])

        for address in info["Net IPvx Address"]:
            if ":" in address:
                self._writer.output(name="Net IPv6 Address", value=address)
            else:
                self._writer.output(name="Net IPv4 Address", value=address)

        for address in info["Net IPvx DNS"]:
            if ":" in address:
                self._writer.output(name="Net IPv6 DNS", value=address)
            else:
                self._writer.output(name="Net IPv4 DNS", value=address)

    def _operatingSystem(self):
        info = self._system.getOsInfo()
        self._writer.output(name="OS Type", value=info["OS Type"])
        self._writer.output(name="OS Name", value=info["OS Name"])
        self._writer.output(name="OS Kernel", value=info["OS Kernel"],
                            comment=info["OS Kernel X"])
        self._writer.output(name="OS Patch", value=info["OS Patch"],
                            comment=info["OS Patch X"])

    def _processors(self):
        info = self._system.getCpuInfo()
        self._writer.output(name="CPU Type", value=info["CPU Type"])
        self._writer.output(name="CPU Addressability", value=info["CPU Addressability"],
                            comment=info["CPU Addressability X"])
        self._writer.output(name="CPU Model", value=info["CPU Model"])
        self._writer.output(name="CPU Sockets", value=info["CPU Sockets"])
        self._writer.output(name="CPU Cores", value=info["CPU Cores"], comment=info["CPU Cores X"])
        self._writer.output(name="CPU Threads", value=info["CPU Threads"],
                            comment=info["CPU Threads X"])
        self._writer.output(name="CPU Clock", value=info["CPU Clock"], comment="MHz")
        self._writer.output(name="CPU Clocks", value=info["CPU Clocks"], comment="MHz")
        for key, value in sorted(info["CPU Cache"].items()):
            self._writer.output(name="CPU L" + key + " Cache", value=value, comment="KB")

    def _systemStatus(self):
        info = self._system.getSysInfo()
        self._writer.output(name="System Platform", value=info["System Platform"],
                            comment=info["System Platform X"])
        self._writer.output(name="System Memory", value=info["System Memory"], comment="MB")
        self._writer.output(name="System Swap Space",
                            value=info["System Swap Space"], comment="MB")
        self._writer.output(name="System Uptime", value=info["System Uptime"])
        self._writer.output(name="System Load", value=info["System Load"],
                            comment="average over last 1min, 5min & 15min")

    def _xwindows(self):
        xwininfo = syslib.Command("xwininfo", pathextra=["/usr/bin/X11", "/usr/openwin/bin"],
                                  args=["-root"], check=False)
        if xwininfo.isFound():
            xwininfo.run(mode="batch")
            if xwininfo.hasOutput():
                xset = syslib.Command("xset", pathextra=["/usr/bin/X11", "/usr/openwin/bin"],
                                      args=["-q"], check=False)
                if xset.isFound():
                    xset.run(mode="batch")
                    try:
                        for line in xset.getOutput():
                            if "Standby:" in line and "Suspend:" in line and "Off:" in line:
                                junk, standby, junk, suspend, junk, off = (line + " ").replace(
                                    " 0 ", " Off ").split()
                                self._writer.output(
                                    name="X-Display Power", value=standby + " " + suspend + " " +
                                    off, comment="DPMS Standby Suspend Off")
                                break
                        for line in xset.getOutput():
                            if "auto repeat delay:" in line and "repeat rate:" in line:
                                self._writer.output(
                                    name="X-Keyboard Repeat", value=line.split()[3],
                                    comment=line.split()[6] + " characters per second")
                                break
                        for line in xset.getOutput():
                            if "acceleration:" in line and "threshold:" in line:
                                self._writer.output(
                                    name="X-Mouse Speed", value=line.split()[1],
                                    comment="acceleration factor")
                                break
                        for line in xset.getOutput():
                            if "timeout:" in line and "cycle:" in line:
                                timeout = int(line.split()[1])
                                if timeout:
                                    self._writer.output(
                                        name="X-Screensaver", value=str(timeout),
                                        comment="no power saving for LCD but can keep CPU busy")
                                break
                    except (IndexError, ValueError):
                        pass

                xrandr = syslib.Command("xrandr", check=False)
                if xrandr.isFound():
                    xrandr.run(mode="batch")
                    for line in xrandr.getOutput():
                        try:
                            if " connected " in line:
                                screen, junk, resolution, *junk, width, junk, height = line.replace(
                                    "mm", "").split()
                                if width in ("0", "160") and height in ("0", "90"):
                                    self._writer.output(name='X-Windows Screen',
                                                        value=screen, comment=resolution)
                                else:
                                    size = math.sqrt(float(width)**2 + float(height)**2) / 25.4
                                    comment = '{0:s}, {1:s}mm x {2:s}mm, {3:3.1f}"'.format(
                                        resolution, width, height, size)
                                    self._writer.output(
                                        name="X-Windows Screen", value=screen, comment=comment)
                        except (IndexError, ValueError):
                            pass

                if "DISPLAY" in os.environ:
                    width = "???"
                    height = "???"
                    try:
                        for line in xwininfo.getOutput():
                            if "Width:" in line:
                                width = line.split()[1]
                            elif "Height:" in line:
                                height = line.split()[1]
                            elif "Depth:" in line:
                                self._writer.output(name="X-Windows Server",
                                                    value=os.environ["DISPLAY"],
                                                    comment=width + "x" + height + ", " +
                                                    line.split()[1] + "bit colour")
                    except IndexError:
                        pass


class OperatingSystem(syslib.Dump):

    def detectLoader(self, writer):
        ldd = syslib.Command("ldd", args=["/bin/sh"], check=False)
        if ldd.isFound():
            ldd.run(filter="libc.*=>", mode="batch")
            if ldd.hasOutput():
                try:
                    glibc = ldd.getOutput()[0].split()[2]
                    version = syslib.info.strings(glibc, "GNU C Library").split(
                        "version")[1].replace(",", " ").split()[0]
                except IndexError:
                    pass
                else:
                    writer.output(name="GNU C library", location=glibc, value=version)

        files = sorted(glob.glob("/lib*/ld*so.*"), reverse=True)
        loaders = []
        for file in files:
            if "/ld-linux" in file:
                loaders.append(file)
        if loaders:
            writer.output(name="Linux Loader", location=" ".join(loaders))

        for version in range(1, 10):
            loaders = []
            for file in files:
                if "/ld-lsb" in file and file.endswith(".so." + str(version)):
                    loaders.append(file)
            if loaders:
                writer.output(name="LSB " + str(version) + ".x Loader", location=" ".join(loaders))

    def hasDevices(self):
        return False

    def hasLoader(self):
        return False

    def getFqdn(self):
        """
        Return fully qualified domain name (ie "hostname.domain.com.").
        """
        fqdn = (socket.getfqdn()).lower()
        if fqdn.count(".") < 2:
            return "Unknown"
        elif fqdn.endswith("."):
            return fqdn
        else:
            return fqdn + "."

    def getNetInfo(self):
        """
        Return network information dictionary.
        """
        info = {}
        info["Net FQDN"] = self.getFqdn()
        info["Net IPvx Address"] = []
        info["Net IPvx DNS"] = []
        return info

    def getOsInfo(self):
        """
        Return operating system information dictionary.
        """
        info = {}
        info["OS Type"] = syslib.info.getSystem()
        info["OS Name"] = "Unknown"
        info["OS Kernel"] = "Unknown"
        info["OS Kernel X"] = ""
        info["OS Patch"] = "Unknown"
        info["OS Patch X"] = ""
        return info

    def getCpuInfo(self):
        """
        Return CPU information dictionary.
        """
        info = {}
        info["CPU Type"] = syslib.info.getMachine()
        info["CPU Addressability"] = "Unknown"
        info["CPU Addressability X"] = ""
        info["CPU Model"] = "Unknown"
        info["CPU Sockets"] = "Unknown"
        info["CPU Cores"] = "Unknown"
        info["CPU Cores X"] = ""
        info["CPU Threads"] = "Unknown"
        info["CPU Threads X"] = ""
        info["CPU Clock"] = "Unknown"
        info["CPU Clocks"] = "Unknown"
        info["CPU Cache"] = {}
        if syslib.info.getMachine() == "x86":
            info["CPU Type"] = "x86"
        elif syslib.info.getMachine() == "x86_64":
            info["CPU Type"] = "x86"
        return info

    def getSysInfo(self):
        """
        Return system information dictionary.
        """
        info = {}
        info["System Platform"] = syslib.info.getPlatform()
        info["System Platform X"] = ""
        info["System Memory"] = "Unknown"
        info["System Swap Space"] = "Unknown"
        info["System Uptime"] = "Unknown"
        info["System Load"] = "Unknown"
        return info

    def _hasValue(self, values, word):
        for key, value in values.items():
            if word in str(value[0]):
                return True
        return False

    def _isitset(self, values, name):
        if name in values:
            return values[name][0]
        else:
            return "Unknown"


class PosixSystem(OperatingSystem):

    def detectDevices(self, writer):
        mount = syslib.Command("mount", check=False)
        if mount.isFound():
            mount.run(filter=":", mode="batch")
            df = syslib.Command("df", flags=["-k"], check=False)
            for line in sorted(mount.getOutput()):
                try:
                    device, junk, directory = line.split()[:3]
                except IndexError:
                    continue
                size = "??? KB"
                if df.isFound():
                    df.setArgs([directory])
                    thread = CommandThread(df)
                    thread.start()
                    endTime = time.time() + 1  # One second delay limit
                    while thread.is_alive():
                        if time.time() > endTime:
                            thread.kill()
                            break
                    try:
                        size = thread.getOutput().split()[-5] + " KB"
                    except IndexError:
                        pass
                writer.output(name="Disk nfs", device="/dev/???", value=size,
                              comment=device + " on " + directory)

    def hasDevices(self):
        return True

    def getFqdn(self):
        """
        Return fully qualified domain name (ie "hostname.domain.com.").
        """
        ispattern = re.compile("\s*(domain|search)\s")
        try:
            with open("/etc/resolv.conf", errors="replace") as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        fqdn = syslib.info.getHostname() + "." + line.split()[1]
                        if fqdn.endswith("."):
                            return fqdn
                        return fqdn + "."
        except (IOError, IndexError):
            pass
        return super().getFqdn()

    def getNetInfo(self):
        """
        Return network information dictionary.
        """
        info = super().getNetInfo()
        ispattern = re.compile("\s*nameserver\s*\d")
        try:
            with open("/etc/resolv.conf", errors="replace") as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        info["Net IPvx DNS"].append(line.split()[1])
        except (IOError, IndexError):
            pass
        return info

    def getOsInfo(self):
        """
        Return operating system information dictionary.
        """
        info = super().getOsInfo()
        info["OS Kernel"] = syslib.info.getKernel()
        info["OS Kernel X"] = syslib.info.getSystem()
        return info

    def getCpuInfo(self):
        """
        Return CPU information dictionary.
        """
        info = super().getCpuInfo()
        return info

    def getSysInfo(self):
        """
        Return system information dictionary.
        """
        info = super().getSysInfo()
        uptime = syslib.Command("uptime", check=False)
        if uptime.isFound():
            uptime.run(mode="batch")
            try:
                info["System Uptime"] = ",".join(uptime.getOutput()[0].split(
                                        ",")[:2]).split("up ")[1].strip()
                info["System Load"] = uptime.getOutput()[0].split(": ")[-1]
            except (IOError, IndexError):
                pass
        return info


class LinuxSystem(PosixSystem):

    def __init__(self):
        self._devices = {}
        lspci = syslib.Command("lspci", pathextra=["/sbin"], args=["-k"], check=False)
        modinfo = syslib.Command("modinfo", pathextra=["/sbin"], check=False)
        if lspci.isFound():
            lspci.run(mode="batch")
            if not lspci.hasOutput():
                lspci.setArgs([])
                lspci.run(mode="batch")
            for line in lspci.getOutput():
                if "Kernel driver in use:" in line:
                    driver = line.split()[-1]
                    if modinfo.isFound():
                        modinfo.setArgs([driver])
                        modinfo.run(filter="^(version|vermagic):", mode="batch")
                        if modinfo.hasOutput():
                            self._devices[device] = (driver + " driver " +
                                                     modinfo.getOutput()[0].split()[1])
                            continue
                    self._devices[device] = driver + " driver"
                elif not line.startswith("\t"):
                    device = line.replace("(", "").replace(")", "")
                    if "VGA compatible controller: " in line:
                        self._devices[device] = ""
                        if "nvidia" in line.lower():
                            try:
                                with open("/proc/driver/nvidia/version", errors="replace") as ifile:
                                    for line in ifile:
                                        if "Kernel Module " in line:
                                            self._devices[device] = (
                                                "nvidia driver " +
                                                line.split("Kernel Module ")[1].split()[0])
                            except IOError:
                                pass
                        elif "VirtualBox" in line and modinfo.isFound():
                            modinfo.setArgs(["vboxvideo"])
                            modinfo.run(filter="^(version|vermagic):", mode="batch")
                            if modinfo.hasOutput():
                                self._devices[device] = ("vboxvideo driver " +
                                                         modinfo.getOutput()[0].split()[1])
                                continue
                    else:
                        self._devices[device] = ""

    def detectDevices(self, writer):

        # Audio device detection
        lines = []
        ispattern = re.compile(" ?\d+ ")
        try:
            with open("/proc/asound/cards", errors="replace") as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        lines.append(line.rstrip("\r\n"))
        except IOError:
            pass
        if lines:
            for line in lines:
                try:
                    card = line.split()[0]
                    model = line.split(": ")[1].split("- ")[-1]
                except IndexError:
                    continue
                for file in sorted(glob.glob("/proc/asound/card" + card + "/pcm*[cp]/info")):
                    try:
                        with open(file, errors="replace") as ifile:
                            for line in ifile:
                                if line.startswith("name: "):
                                    name = model + " " + line.rstrip(
                                        "\r\n").replace("name: ", "", 1)
                    except (IOError, IndexError):
                        continue
                    device = "/dev/snd/pcmC" + card + "D" + os.path.dirname(file).split("pcm")[-1]
                    if os.path.exists(device):
                        if device.endswith("p"):
                            writer.output(name="Audio device", device=device, value=name,
                                          comment="SPK")
                        else:
                            writer.output(name="Audio device", device=device, value=name,
                                          comment="MIC")
                    else:
                        if card == "0":
                            unit = ""
                        else:
                            unit = card
                        if glob.glob("/proc/asound/card" + card + "/midi*"):
                            device = "/dev/midi" + unit
                            if not os.path.exists(device):
                                device = "/dev/???"
                            writer.output(name="Audio device", device=device, value=model,
                                          comment="MIDI")
                        device = "/dev/dsp" + unit
                        if not os.path.exists(device):
                            device = "/dev/???"
                        if glob.glob("/proc/asound/card" + card + "/pcm*c"):
                            if glob.glob("/proc/asound/card" + card + "/pcm*p"):
                                writer.output(name="Audio device", device=device, value=model,
                                              comment="MIC/SPK")
                            else:
                                writer.output(name="Audio device", device=device, value=model,
                                              comment="MIC")
                        elif glob.glob("/proc/asound/card" + card + "/pcm*p"):
                            writer.output(name="Audio device", device=device, value=model,
                                          comment="SPK")

        # Battery detection
        batteries = []
        if os.path.isdir("/sys/class/power_supply"):
            for directory in glob.glob("/sys/class/power_supply/BAT*"):  # New kernels
                batteries.append(BatteryPower(directory))
        else:
            for directory in glob.glob("/proc/acpi/battery/BAT*"):
                batteries.append(BatteryAcpi(directory))
        for battery in batteries:
            if battery.isExist():
                model = (
                    battery.getOem() + " " + battery.getName() + " " + battery.getType() + " " +
                    str(battery.getCapacityMax()) + "mAh/" + str(battery.getVoltage()) + "mV")
                if battery.getCharge() == "-":
                    state = "-"
                    if battery.getRate() > 0:
                        state += str(battery.getRate()) + "mA"
                        if battery.getVoltage() > 0:
                            mywatts = "{0:4.2f}".format(
                                float(battery.getRate()*battery.getVoltage()) / 1000000)
                            state += ", " + str(mywatts) + "W"
                        hours = "{0:3.1f}".format(float(battery.getCapacity()) / battery.getRate())
                        state += ", " + str(hours) + "h"
                elif battery.getCharge() == "+":
                    state = "+"
                    if battery.getRate() > 0:
                        state += str(battery.getRate()) + "mA"
                        if battery.getVoltage() > 0:
                            mywatts = "{0:4.2f}".format(float(battery.getRate() *
                                                        battery.getVoltage()) / 1000000)
                            state += ", " + str(mywatts) + "W"
                else:
                    state = "Unused"
                writer.output(name="Battery device", device="/dev/???",
                              value=str(battery.getCapacity()) + "mAh",
                              comment=model + " [" + state + "]")

        # CD device detection
        for directory in sorted(glob.glob("/proc/ide/hd*")):
            try:
                with open(os.path.join(directory, "driver"), errors="replace") as ifile:
                    for line in ifile:
                        if line.startswith("ide-cdrom "):
                            with open(os.path.join(directory, "model"), errors="replace") as ifile:
                                model = ifile.readline().strip()
                                writer.output(name="CD device", device="/dev/" +
                                              os.path.basename(directory), value=model)
                                break
            except IOError:
                pass
        if os.path.isdir("/sys/bus/scsi/devices"):
            for file in sorted(glob.glob("/sys/block/sr*/device")):  # New kernels
                try:
                    id = os.path.basename(os.readlink(file))
                except OSError:
                    continue
                try:
                    if os.path.isdir("/sys/bus/scsi/devices/" + id):
                        with open(os.path.join("/sys/bus/scsi/devices", id, "vendor"),
                                  errors="replace") as ifile:
                            model = ifile.readline().strip()
                        with open(os.path.join("/sys/bus/scsi/devices", id, "model"),
                                  errors="replace") as ifile:
                            model += " " + ifile.readline().strip()
                except IOError:
                    model = "???"
                device = "/dev/" + os.path.basename(os.path.dirname(file))
                writer.output(name="CD device", device=device, value=model)
        else:
            model = "???"
            unit = 0
            isjunk = re.compile(".*Vendor: | *Model:| *Rev: .*")
            try:
                with open("/proc/scsi/scsi", errors="replace") as ifile:
                    for line in ifile:
                        if "Vendor: " in line and "Model: " in line:
                            model = isjunk.sub("", line.rstrip("\r\n"))
                        elif "Type:" in line and "CD-ROM" in line:
                            if os.path.exists("/dev/sr" + str(unit)):
                                device = "/dev/sr" + str(unit)
                            else:
                                device = "/dev/scd" + str(unit)
                            writer.output(name="CD device", device=device, value=model)
                            model = "???"
                            unit += 1
            except IOError:
                pass

        # Disk device detection
        uuids = {}
        for file in glob.glob("/dev/disk/by-uuid/*"):
            try:
                uuids["/dev/" + os.path.basename(os.readlink(file))] = file
            except OSError:
                pass

        mount = syslib.Command("mount", check=False)
        if mount.isFound():
            mount.run(filter="^/dev/", mode="batch")
        partitions = []
        try:
            with open("/proc/partitions", errors="replace") as ifile:
                for line in ifile:
                    partitions.append(line.rstrip("\r\n"))
        except IOError:
            pass
        swaps = []
        try:
            with open("/proc/swaps", errors="replace") as ifile:
                for line in ifile:
                    if line.startswith("/dev/"):
                        swaps.append(line.split()[0])
        except IOError:
            pass
        for directory in sorted(glob.glob("/proc/ide/hd*")):
            try:
                with open(os.path.join(directory, "driver"), errors="replace") as ifile:
                    for line in ifile:
                        if line.startswith("ide-disk "):
                            with open(os.path.join(directory, "model"), errors="replace") as ifile2:
                                model = ifile2.readline().rstrip("\r\n")
                            hdx = os.path.basename(directory)
                            for partition in partitions:
                                if partition.endswith(hdx) or hdx + " " in partition:
                                    try:
                                        size = partition.split()[2]
                                    except IndexError:
                                        size = "???"
                                    writer.output(name="Disk device", device="/dev/" + hdx,
                                                  value=size + " KB", comment=model)
                                elif hdx in partition:
                                    size, hdxn = partition.split()[2:4]
                                    device = "/dev/" + hdxn
                                    comment = ""
                                    if device in swaps:
                                        comment = "swap"
                                    for line2 in mount.getOutput():
                                        if line2.startswith(device + " "):
                                            try:
                                                mountPoint, junk, mountType = line2.split()[2:5]
                                                comment = mountType + " on " + mountPoint
                                            except (IndexError, ValueError):
                                                comment = "??? on ???"
                                            break
                                    writer.output(name="Disk device", device=device,
                                                  value=size + " KB", comment=comment)
            except IOError:
                pass
        if os.path.isdir("/sys/bus/scsi/devices"):
            for file in sorted(glob.glob("/sys/block/sd*/device")):  # New kernels
                try:
                    id = os.path.basename(os.readlink(file))
                except OSError:
                    continue
                try:
                    if os.path.isdir("/sys/bus/scsi/devices/" + id):
                        with open(os.path.join("/sys/bus/scsi/devices", id, "vendor"),
                                  errors="replace") as ifile:
                            model = ifile.readline().strip()
                        with open(os.path.join("/sys/bus/scsi/devices", id, "model"),
                                  errors="replace") as ifile:
                            model += " " + ifile.readline().strip()
                except IOError:
                    model = "???"
                sdx = os.path.basename(os.path.dirname(file))
                for partition in partitions:
                    if partition.endswith(sdx) or sdx + " " in partition:
                        try:
                            size = partition.split()[2]
                        except IndexError:
                            size = "???"
                        writer.output(name="Disk device", device="/dev/" + sdx, value=size + " KB",
                                      comment=model)
                    elif sdx in partition:
                        size, sdxn = partition.split()[2:4]
                        device = "/dev/" + sdxn
                        comment = ""
                        if device in swaps:
                            comment = "swap"
                        for line2 in mount.getOutput():
                            try:
                                if (line2.startswith(device + " ") or
                                        line2.startswith(uuids[device] + " ")):
                                    try:
                                        mountPoint, junk, mountType = line2.split()[2:5]
                                        comment = mountType + " on " + mountPoint
                                    except (IndexError, ValueError):
                                        comment = "??? on ???"
                                    break
                            except KeyError:
                                pass
                        writer.output(name="Disk device", device=device, value=size + " KB",
                                      comment=comment)
        else:
            model = "???"
            unit = 0
            isjunk = re.compile(".*Vendor: | *Model:| *Rev: .*")
            try:
                with open("/proc/scsi/scsi", errors="replace") as ifile:
                    for line in ifile:
                        if "Vendor: " in line and "Model: " in line:
                            model = isjunk.sub("", line.rstrip("\r\n"))
                        elif "Type:" in line and "Direct-Access" in line:
                            sdx = "sd" + chr(97 + unit)
                            if os.path.exists("/dev/" + sdx):
                                for partition in partitions:
                                    if partition.endswith(sdx) or sdx + " " in partition:
                                        try:
                                            size = partition.split()[2]
                                        except IndexError:
                                            size = "???"
                                        writer.output(name="Disk device", device="/dev/" + sdx,
                                                      value=size + " KB", comment=model)
                                    elif sdx in partition:
                                        size, sdxn = partition.split()[2:4]
                                        device = "/dev/" + sdxn
                                        comment = ""
                                        if device in swaps:
                                            comment = "swap"
                                        for line2 in mount.getOutput():
                                            if line2.startswith(device + " "):
                                                try:
                                                    mountPoint, junk, mountType = line2.split()[2:5]
                                                    comment = mountType + " on " + mountPoint
                                                except (IndexError, ValueError):
                                                    comment = "??? on ???"
                                                break
                                        writer.output(name="Disk device", device=device,
                                                      value=size + " KB", comment=comment)
                            model = "???"
                            unit += 1
            except IOError:
                pass

        # Disk mounts detection
        super().detectDevices(writer)

        # Ethernet device detection
        for line, device in sorted(self._devices.items()):
            if "Ethernet controller: " in line:
                model = line.split("Ethernet controller: ")[1].replace(
                    "Semiconductor ", "").replace("Co., ", "").replace(
                    "Ltd. ", "").replace("PCI Express ", "")
                writer.output(name="Ethernet device", device="/dev/???", value=model,
                              comment=device)

        # Firewire device detection
        for line, device in sorted(self._devices.items()):
            if "FireWire (IEEE 1394): " in line:
                model = line.split("FireWire (IEEE 1394): ")[1]
                writer.output(name="Firewire device", device="/dev/???", value=model,
                              comment=device)

        # Graphics device detection
        for line, device in sorted(self._devices.items()):
            if "VGA compatible controller: " in line:
                model = line.split("VGA compatible controller: ")[1].strip()
                writer.output(name="Graphics device", device="/dev/???", value=model,
                              comment=device)

        # InifiniBand device detection
        for line, device in sorted(self._devices.items()):
            if "InfiniBand: " in line:
                model = line.split("InfiniBand: ")[1].replace("InfiniHost", "InifiniBand")
                writer.output(name="InifiniBand device", device="/dev/???", value=model,
                              comment=device)

        # Input device detection
        info = {}
        for file in glob.glob("/dev/input/by-path/*event*"):
            try:
                device = "/dev/input/" + os.path.basename(os.readlink(file))
                if os.path.exists(device):
                    info[device] = os.path.basename(file).replace("-event", "").replace("-", " ")
            except OSError:
                continue
        isjunk = re.compile("/usb-\w{4}_\w{4}-")
        for file in glob.glob("/dev/input/by-id/*event*"):
            try:
                device = "/dev/input/" + os.path.basename(os.readlink(file))
                if os.path.exists(device) and not isjunk.search(file):
                    info[device] = os.path.basename(file).split("-")[1].replace("_", " ")
            except (IndexError, OSError):
                continue
        for key, value in sorted(info.items()):
            writer.output(name="Input device", device=key, value=value)

        # Network device detection
        for line, device in sorted(self._devices.items()):
            if "Network controller: " in line:
                model = line.split(": ", 1)[1].split(" (")[0]
                writer.output(name="Network device", device="/dev/???", value=model,
                              comment=device)

        # Video device detection
        for directory in sorted(glob.glob("/sys/class/video4linux/*")):
            device = os.path.basename(directory)
            try:
                with open(os.path.join(directory, "name"), errors="replace") as ifile:
                    writer.output(name="Video device", device="/dev/" + device,
                                  value=ifile.readline().rstrip("\r\n"))
                    continue
            except IOError:
                pass
            writer.output(name="Video device", device="/dev/" + device, value="???")

    def hasLoader(self):
        return True

    def getNetInfo(self):
        """
        Return network information dictionary.
        """
        info = super().getNetInfo()
        env = {}
        if "LANG" not in os.environ:
            env["LANG"] = "en_US"
        ifconfig = syslib.Command(file="/sbin/ifconfig", args=["-a"])
        ifconfig.run(env=env, filter="inet[6]? addr", mode="batch")
        isjunk = re.compile(".*inet[6]? addr[a-z]*:")
        for line in ifconfig.getOutput():
            info["Net IPvx Address"].append(isjunk.sub(" ", line).split()[0])
        return info

    def getOsInfo(self):
        """
        Return operating system information dictionary.
        """
        info = super().getOsInfo()
        if os.path.isfile("/etc/redhat-release"):
            try:
                with open("/etc/redhat-release", errors="replace") as ifile:
                    info["OS Name"] = ifile.readline().rstrip("\r\n")
            except IOError:
                pass
            return info
        elif os.path.isfile("/etc/SuSE-release"):
            try:
                with open("/etc/SuSE-release", errors="replace") as ifile:
                    info["OS Name"] = ifile.readline().rstrip("\r\n")
                    for line in ifile:
                        if "PATCHLEVEL" in line:
                            try:
                                info["OS Patch"] = line.split()[-1]
                                break
                            except IndexError:
                                pass
                return info
            except IOError:
                info["OS Name"] = "Unknown"
            return info
        elif os.path.isfile("/etc/lsb-release"):
            try:
                with open("/etc/lsb-release", errors="replace") as ifile:
                    lines = []
                    for line in ifile:
                        lines.append(line.rstrip("\r\n"))
            except IOError:
                pass
            else:
                if lines and lines[-1].startswith("DISTRIB_DESCRIPTION="):
                    info["OS Name"] = lines[-1].split("=")[1].replace('"', '')
                    return info
                else:
                    id = None
                    for line in lines:
                        if line.startswith("DISTRIB_ID="):
                            id = line.split("=")[1]
                        elif line.startswith("DISTRIB_RELEASE=") and id:
                            info["OS Name"] = id + " " + line.split("=")[1]
                            return info
        files = sorted(glob.glob("/etc/*release"))
        if os.path.isfile("/etc/kanotix-version"):
            try:
                with open("/etc/kanotix-version", errors="replace") as ifile:
                    info["OS Name"] = "Kanotix " + ifile.readline().rstrip("\r\n").split()[1]
            except (IOError, IndexError):
                pass
            return info
        elif os.path.isfile("/etc/knoppix-version"):
            try:
                with open("/etc/knoppix-version", errors="replace") as ifile:
                    info["OS Name"] = "Knoppix " + ifile.readline().rstrip("\r\n").split()[0]
            except (IOError, IndexError):
                pass
            return info
        elif os.path.isfile("/etc/debian_version"):
            try:
                with open("/etc/debian_version", errors="replace") as ifile:
                    info["OS Name"] = "Debian " + ifile.readline().rstrip(
                        "\r\n").split("=")[-1].replace('"', '')
            except IOError:
                pass
            return info
        elif os.path.isfile("/etc/DISTRO_SPECS"):
            try:
                id = None
                with open("/etc/DISTRO_SPECS", errors="replace") as ifile:
                    for line in ifile:
                        if line.startswith("DISTRO_NAME"):
                            id = line.rstrip("\r\n").split("=")[1].replace("'", "")
                        elif line.startswith("DISTRO_VERSION") and id:
                            info["OS Name"] = id + " " + line.rstrip("\r\n").split("=")[1]
                            return info
            except (IOError, IndexError):
                pass
            return info
        dpkg = syslib.Command("dpkg", check=False, args=["--list"])
        if dpkg.isFound():
            dpkg.run(mode="batch")
            for line in dpkg.getOutput():
                try:
                    package = line.split()[1]
                    if package == "knoppix-g":
                        info["OS Name"] = "Knoppix " + line.split()[2].split("-")[0]
                        return info
                    elif package == "mepis-auto":
                        info["OS Name"] = "MEPIS " + line.split()[2]
                        return info
                    elif " kernel " in line and "MEPIS" in line:
                        isjunk = re.compile("MEPIS.")
                        info["OS Name"] = "MEPIS " + isjunk.sub("", line.split()[2])
                        return info
                except IndexError:
                    pass
            for line in dpkg.getOutput():
                try:
                    package = line.split()[1]
                    if package == "base-files":
                        info["OS Name"] = "Debian " + line.split()[2]
                        return info
                except IndexError:
                    pass
            return info
        return info

    def getCpuInfo(self):
        """
        Return CPU information dictionary.
        """
        info = super().getCpuInfo()
        isspace = re.compile("\s+")

        if info["CPU Addressability"] == "Unknown":
            if syslib.info.getMachine().endswith("64"):
                info["CPU Addressability"] = "64bit"
            else:
                info["CPU Addressability"] = "32bit"

        try:
            with open("/proc/cpuinfo", errors="replace") as ifile:
                lines = []
                for line in ifile:
                    lines.append(line.rstrip("\r\n"))
        except IOError:
            pass
        try:
            if syslib.info.getMachine() == "Power":
                for line in lines:
                    if line.startswith("cpu"):
                        info["CPU Model"] = "PowerPC_" + isspace.sub(" ",
                                            line.split(": ")[1].split(" ")[0].strip())
                        break
            if info["CPU Model"] == "Unknown":
                for line in lines:
                    if line.startswith("model name"):
                        info["CPU Model"] = isspace.sub(" ", line.split(": ")[1].strip())
                        break
            if syslib.info.getMachine() == "x86_64":
                for line in lines:
                    if line.startswith("address size"):
                        info["CPU Addressability X"] = line.split(
                            ":")[1].split()[0] + "bit physical"
        except (IOError, IndexError):
            pass

        try:
            threads = len(glob.glob("/sys/devices/system/cpu/cpu[0-9]*"))
        except (IndexError, ValueError):
            threads = 0
        if not threads:
            for line in lines:
                if line.startswith("processor"):
                    threads += 1

        vitualMachine = self._getVirtualMachine()
        if vitualMachine:
            info["CPU Cores"] = str(threads)
            info["CPU Cores X"] = vitualMachine + " VM"
            info["CPU Threads"] = info["CPU Cores"]
            info["CPU Threads X"] = info["CPU Cores X"]
        else:
            found = []
            for file in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/topology/physical_package_id"):
                try:
                    with open(file, errors="replace") as ifile:
                        line = ifile.readline().rstrip("\r\n")
                        if line not in found:
                            found.append(line)
                except IOError:
                    pass
            if found:
                sockets = len(found)
            else:
                for line in lines:
                    if line.startswith("physical id"):
                        if line not in found:
                            found.append(line)
                if found:
                    sockets = len(found)
                else:
                    sockets = threads
                    for line in lines:
                        if line.startswith("siblings"):
                            try:
                                sockets = threads / int(line.split()[2])
                            except (IndexError, ValueError):
                                pass
                            break
            try:
                with open("/sys/devices/system/cpu/cpu0/topology/thread_siblings_list",
                          errors="replace") as ifile:
                    cpuCores = int(threads/(int(ifile.readline().rstrip(
                        "\r\n").split("-")[-1]) + 1))
            except (IOError, ValueError):
                coresPerSocket = None
                if "Dual Core" in info["CPU Model"]:
                    coresPerSocket = 2
                elif "Quad-Core" in info["CPU Model"]:
                    coresPerSocket = 4
                else:
                    for line in lines:
                        if line.startswith("cpu cores"):
                            try:
                                coresPerSocket = int(line.split()[3])
                                if coresPerSocket == 1:
                                    coresPerSocket = None
                            except (IndexError, ValueError):
                                pass
                            break
                if coresPerSocket:
                    cpuCores = sockets * coresPerSocket
                else:
                    cpuCores = sockets
            info["CPU Sockets"] = str(sockets)
            info["CPU Cores"] = str(cpuCores)
            info["CPU Threads"] = str(threads)
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq",
                      errors="replace") as ifile:
                info["CPU Clock"] = str(int(int(ifile.readline().rstrip("\r\n")) / 1000 + 0.5))
        except (IOError, ValueError):
            for line in lines:
                if line.startswith("cpu MHz"):
                    try:
                        info["CPU Clock"] = str(int(float(line.split(": ")[1]) + 0.5))
                    except (IndexError, ValueError):
                        pass
                    break
            if info["CPU Clock"] == "Unknown":
                for line in lines:
                    if line.startswith("clock"):
                        try:
                            info["CPU Clock"] = str(int(float(line.split(": ")[1]) + 0.5))
                        except (IndexError, ValueError):
                            pass
                        break
        found = []
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies",
                      errors="replace") as ifile:
                for clock in ifile.readline().rstrip("\r\n").split():
                    found.append(str(int(int(clock) / 1000 + 0.5)))
                if found:
                    info["CPU Clocks"] = " ".join(found)
        except (IOError, ValueError):
            try:
                with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq",
                          errors="replace") as ifile:
                    info["CPU Clocks"] = str(int(int(ifile.readline()) / 1000 + 0.5))
                with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq",
                          errors="replace") as ifile:
                    info["CPU Clocks"] += " " + str(int(int(ifile.readline()) / 1000 + 0.5))
            except (IOError, ValueError):
                info["CPU Clocks"] = "Unknown"
        for cache in sorted(glob.glob("/sys/devices/system/cpu/cpu0/cache/index*")):
            try:
                with open(os.path.join(cache, "level"), errors="replace") as ifile:
                    level = ifile.readline().rstrip("\r\n")
                with open(os.path.join(cache, "type"), errors="replace") as ifile:
                    type = ifile.readline().rstrip("\r\n")
                if type == "Data":
                    level += "d"
                elif type == "Instruction":
                    level += "i"
                with open(os.path.join(cache, "size"), errors="replace") as ifile:
                    info["CPU Cache"][level] = str(int(ifile.readline().rstrip("\r\nK")))
            except (IOError, ValueError):
                pass
        if not info["CPU Cache"]:
            for line in lines:
                if line.startswith("cache size"):
                    try:
                        info["CPU Cache"]["?"] = str(int(float(line.split()[3])))
                    except (IndexError, ValueError):
                        pass
                    break
        return info

    def getSysInfo(self):
        """
        Return system information dictionary.
        """
        info = super().getSysInfo()
        try:
            with open("/proc/meminfo", errors="replace") as ifile:
                try:
                    for line in ifile:
                        if line.startswith("MemTotal:"):
                            info["System Memory"] = str(int(float(line.split()[1]) / 1024 + 0.5))
                        elif line.startswith("SwapTotal:"):
                            info["System Swap Space"] = str(int(float(line.split()[1]) /
                                                                1024 + 0.5))
                except (IndexError, ValueError):
                    pass
        except IOError:
            pass
        return info

    def _getVirtualMachine(self):
        if os.path.isdir("/sys/devices/xen"):
            return "Xen"

        for line in self._devices:
            if "RHEV" in line:
                return "RHEV"
            elif "VirtualBox" in line:
                return "VirtualBox"
            elif "VMWare" in line or "VMware" in line:
                return "VMware"
            elif " Xen " in line in line:
                return "Xen"

        for file in (glob.glob("/sys/bus/scsi/devices/*/model") + ["/proc/scsi/scsi"] +
                     glob.glob("/proc/ide/hd?/model")):
            try:
                with open(file, errors="replace") as ifile:
                    for line in ifile:
                        if "RHEV" in line:
                            return "RHEV"
                        elif "VBOX " in line:
                            return "VirtualBox"
                        elif "VMWare " in line or "VMware " in line:
                            return "VMware"
            except IOError:
                pass
        return None


class WindowsSystem(OperatingSystem):

    def __init__(self):
        pathextra = []
        if "WINDIR" in os.environ:
            pathextra.append(os.path.join(os.environ["WINDIR"], "system32"))
        self._ipconfig = syslib.Command("ipconfig", pathextra=pathextra, args=["-all"])
        # Except for WIndows XP Home
        self._systeminfo = syslib.Command("systeminfo", pathextra=pathextra, check=False)

    def getFqdn(self):
        """
        Return fully qualified domain name (ie "hostname.domain.com.").
        """
        if not self._ipconfig.hasOutput():
            self._ipconfig.run(mode="batch")
        for line in self._ipconfig.getOutput("Connection-specific DNS Suffix"):
            fqdn = syslib.info.getHostname() + "." + line.split()[-1]
            if fqdn.count(".") > 1:
                if fqdn.endswith("."):
                    return fqdn
                return fqdn + "."
        return super().getFqdn()

    def getNetInfo(self):
        """
        Return network information dictionary.
        """
        info = {}
        info["Net FQDN"] = self.getFqdn()
        if not self._ipconfig.hasOutput():
            self._ipconfig.run(mode="batch")
        info["Net IPvx Address"] = []
        for line in self._ipconfig.getOutput("IP.* Address"):
            (info["Net IPvx Address"]).append(line.replace("(Preferred)", "").split()[-1])
        info["Net IPvx DNS"] = []
        for line in self._ipconfig.getOutput():
            if "DNS Servers" in line:
                (info["Net IPvx DNS"]).append(line.split()[-1])
            elif info["Net IPvx DNS"]:
                if " : " in line:
                    break
                (info["Net IPvx DNS"]).append(line.split()[-1])
        return info

    def getOsInfo(self):
        """
        Return operating system information dictionary.
        """
        info = {}
        info["OS Type"] = "windows"
        info["OS Kernel X"] = "NT"
        subkeys, values = self._regRead(winreg.HKEY_LOCAL_MACHINE,
                                        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        info["OS Name"] = self._isitset(values, "ProductName")
        info["OS Kernel"] = syslib.info.getKernel()
        info["OS Patch"] = self._isitset(values, "CSDVersion")
        patchNumber = self._isitset(values, "CSDBuildNumber")
        if patchNumber == "Unknown":
            info["OS Patch X"] = ""
        else:
            info["OS Patch X"] = patchNumber
        return info

    def getCpuInfo(self):
        """
        Return CPU information dictionary.
        """
        info = super().getCpuInfo()
        subkeys, values = self._regRead(winreg.HKEY_LOCAL_MACHINE,
                                        r"HARDWARE\DESCRIPTION\System\CentralProcessor")
        info["CPU Cores"] = str(len(subkeys))
        info["CPU Threads"] = info["CPU Cores"]
        subkeys, values = self._regRead(winreg.HKEY_LOCAL_MACHINE,
                                        r"HARDWARE\DESCRIPTION\System\BIOS")
        if self._systeminfo.isFound():
            self._systeminfo.run(mode="batch")
        if self._hasValue(values, "RHEV") or self._systeminfo.isMatchOutput("RHEV"):
            info["CPU Cores X"] = "RHEV VM"
        elif self._hasValue(values, "VMware") or self._systeminfo.isMatchOutput("VMware"):
            info["CPU Cores X"] = "VMware VM"
        elif self._hasValue(values, "VirtualBox") or self._systeminfo.isMatchOutput("VirtualBox"):
            info["CPU Cores X"] = "VirtualBox VM"
        subkeys, values = self._regRead(winreg.HKEY_LOCAL_MACHINE,
                                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        info["CPU Model"] = re.sub(" +", " ", self._isitset(values, "ProcessorNameString").strip())
        info["CPU Clock"] = str(self._isitset(values, "~MHz"))
        return info

    def getSysInfo(self):
        """
        Return system information dictionary.
        """
        info = super().getSysInfo()
        if self._systeminfo.isFound():
            self._systeminfo.run(mode="batch")
        memory = self._systeminfo.getOutput(":.*MB$")
        if len(memory) > 0:
            info["System Memory"] = memory[0].split()[-2].replace(",", "")
        if len(memory) > 2:
            info["System Swap Space"] = memory[4].split()[-2].replace(",", "")
        try:
            uptime = self._systeminfo.getOutput("^System Up Time:")[0].split()
            info["System Uptime"] = (uptime[3] + " days " + uptime[5].zfill(2) +
                                     ":" + uptime[7].zfill(2))
        except IndexError:
            pass
        info["System Load"] = "Unknown"
        return info

    def _regRead(self, hive, path):
        subkeys = []
        values = {}
        try:
            key = winreg.OpenKey(hive, path)
        except WindowsError:
            pass
        else:
            nsubkeys, nvalues, address = winreg.QueryInfoKey(key)
            for i in range(nsubkeys):
                subkeys.append(winreg.EnumKey(key, i))
            for i in range(nvalues):
                name, value, type = winreg.EnumValue(key, i)
                values[name] = [value, type]
        return subkeys, values


class Writer(syslib.Dump):

    def __init__(self, options):
        self._options = options

    def output(self, name, architecture="", comment="", device="", location="", value=""):
        line = " {0:19s}".format(name + ":")
        if device:
            line += (" {0:12s}".format(device)) + " " + value
        elif location:
            line += " " + location
            if value:
                line += "  " + value
        elif value:
            line += " " + value
        if architecture:
            line += " (" + architecture + ")"
        if comment:
            line += " (" + comment + ")"
        print(line)


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Detect(options).run()
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
            files = glob.glob(arg)  # Fixes Windows globbing bug
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
