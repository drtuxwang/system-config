#!/usr/bin/env python3
"""
System configuration detection tool.

1996-2021 By Dr Colin Kong
"""

import functools
import glob
import json
import math
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Generator, List, Tuple

import command_mod
import file_mod
import power_mod
import subtask_mod

if os.name == 'nt':
    import winreg  # pylint: disable = import-error

RELEASE = '5.16.7'
VERSION = 20211109

# pylint: disable = too-many-lines


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release_date = (
            f'{str(VERSION)[:4]}-{str(VERSION)[4:6]}-{str(VERSION)[6:]}'
        )
        self._release_version = RELEASE

        self._system = OperatingSystem.factory()

    def get_release_date(self) -> str:
        """
        Return release date.
        """
        return self._release_date

    def get_release_version(self) -> str:
        """
        Return release version.
        """
        return self._release_version

    def get_system(self) -> 'OperatingSystem':
        """
        Return operating system.
        """
        return self._system


class CommandThread(threading.Thread):
    """
    Command thread class
    """

    def __init__(self, command: command_mod.Command) -> None:
        threading.Thread.__init__(self, daemon=True)
        self._child: subprocess.Popen = None
        self._command = command
        self._stdout = ''

    def run(self) -> None:
        """
        Run thread
        """
        self._child = subtask_mod.Child(self._command.get_cmdline()).run()
        while True:
            try:
                byte = self._child.stdout.read(1)
            except AttributeError:
                continue
            if not byte:
                break
            self._stdout += byte.decode('utf-8', 'replace')

    def kill(self) -> None:
        """
        Kill thread
        """
        if self._child:
            self._child.kill()
            self._child = None

    def get_output(self) -> str:
        """
        Return thread output.
        """
        return self._stdout


class Detect:
    """
    Detect class
    """

    def __init__(self, options: Options) -> None:
        self._author = (
            f'Sysinfo {options.get_release_version()} '
            f'({options.get_release_date()})'
        )

        self._system = options.get_system()

    def _network_information(self) -> None:
        info = self._system.get_net_info()
        Writer.output(
            name='Hostname',
            value=socket.gethostname().split('.')[0].lower(),
        )
        Writer.output(name='Net FQDN', value=info['Net FQDN'])

        for address in info['Net IPvx Address']:
            if ':' in address:
                Writer.output(name='Net IPv6 Address', value=address)
            else:
                Writer.output(name='Net IPv4 Address', value=address)

        for address in info['Net IPvx DNS']:
            if ':' in address:
                Writer.output(name='Net IPv6 DNS', value=address)
            else:
                Writer.output(name='Net IPv4 DNS', value=address)

    def _operating_system(self) -> None:
        info = self._system.get_os_info()
        Writer.output(name='OS Type', value=info['OS Type'])
        Writer.output(name='OS Name', value=info['OS Name'])
        Writer.output(
            name='OS Kernel',
            value=info['OS Kernel'],
            comment=info['OS Kernel X'],
        )
        Writer.output(
            name='OS Patch',
            value=info['OS Patch'],
            comment=info['OS Patch X'],
        )
        Writer.output(name='OS Boot Time', value=info['OS Boot'])

    def _processors(self) -> None:
        info = self._system.get_cpu_info()
        Writer.output(name='CPU Type', value=info['CPU Type'])
        Writer.output(
            name='CPU Addressability',
            value=info['CPU Addressability'],
            comment=info['CPU Addressability X'],
        )
        Writer.output(name='CPU Model', value=info['CPU Model'])
        Writer.output(name='CPU Sockets', value=info['CPU Sockets'])
        Writer.output(
            name='CPU Cores',
            value=info['CPU Cores'],
            comment=info['CPU Cores X'],
        )
        Writer.output(
            name='CPU Threads',
            value=info['CPU Threads'],
            comment=info['CPU Threads X'],
        )
        Writer.output(name='CPU Clock', value=info['CPU Clock'], comment='MHz')
        Writer.output(
            name='CPU Clocks',
            value=info['CPU Clocks'],
            comment='MHz',
        )
        for key, value in sorted(info['CPU Cache'].items()):
            Writer.output(
                name=f'CPU L{key} Cache',
                value=value,
                comment='KB',
            )

    def _system_status(self) -> None:
        info = self._system.get_sys_info()
        Writer.output(
            name='System Platform',
            value=info['System Platform'],
            comment=info['System Platform X'],
        )
        Writer.output(
            name='System Memory',
            value=info['System Memory'],
            comment='MB',
        )
        Writer.output(
            name='System Swap Space',
            value=info['System Swap Space'],
            comment='MB',
        )
        Writer.output(name='System Uptime', value=info['System Uptime'])
        Writer.output(
            name='System Load',
            value=info['System Load'],
            comment='average over last 1min, 5min & 15min',
        )

    @staticmethod
    def _xset() -> None:
        xset = command_mod.Command(
            'xset',
            pathextra=['/usr/bin/X11', '/usr/openwin/bin'],
            args=['-q'],
            errors='ignore'
        )
        if xset.is_found():
            task = subtask_mod.Batch(xset.get_cmdline())
            task.run()
            try:
                for line in task.get_output():
                    if ('Standby:' in line and
                            'Suspend:' in line and
                            'Off:' in line):
                        _, standby, _, suspend, _, off = (line + ' ').replace(
                            ' 0 ', ' Off ').split()
                        Writer.output(
                            name='X-Display Power',
                            value=f'{standby} {suspend} {off}',
                            comment='DPMS Standby Suspend Off',
                        )
                        break
                for line in task.get_output():
                    if 'auto repeat delay:' in line and 'repeat rate:' in line:
                        Writer.output(
                            name='X-Keyboard Repeat',
                            value=line.split()[3],
                            comment=line.split()[6] + ' characters per second',
                        )
                        break
                for line in task.get_output():
                    if 'acceleration:' in line and 'threshold:' in line:
                        Writer.output(
                            name='X-Mouse Speed',
                            value=line.split()[1],
                            comment='acceleration factor',
                        )
                        break
                for line in task.get_output():
                    if 'timeout:' in line and 'cycle:' in line:
                        timeout = int(line.split()[1])
                        if timeout:
                            Writer.output(
                                name='X-Screensaver',
                                value=str(timeout),
                                comment='no power saving for LCD but can '
                                'keep CPU busy',
                            )
                        break
            except (IndexError, ValueError):
                pass

    @staticmethod
    def _xdisplay(display: str) -> None:
        xrandr = command_mod.Command('xrandr', errors='ignore')
        if xrandr.is_found():
            task = subtask_mod.Batch(xrandr.get_cmdline())
            task.run(pattern='^Screen .* current | connected ')
            for line in task.get_output():
                try:
                    if line.startswith('Screen ') and ' current ' in line:
                        comment = line.split(
                            'current ')[-1].split(',')[0].replace(' ', '')
                        Writer.output(
                            name='X-Windows Display',
                            value=display,
                            comment=comment,
                        )
                    elif ' connected ' in line:
                        columns = line.replace(
                            'primary ', '').replace('mm', '').split()
                        screen, _, resolution, *_, width, _, height = columns
                        if (width, height) == ('0', '0'):
                            Writer.output(
                                name="X-Windows Screen",
                                value=screen,
                                comment=resolution,
                            )
                        else:
                            size = math.sqrt(
                                float(width)**2 + float(height)**2) / 25.4
                            comment = (
                                f'{resolution}, {width}mm x {height}mm, '
                                f'{size:3.1f}"'
                            )
                            Writer.output(
                                name='X-Windows Screen',
                                value=screen,
                                comment=comment,
                            )
                except (IndexError, ValueError):
                    pass
        else:
            xwininfo = command_mod.Command(
                'xwininfo',
                pathextra=['/usr/bin/X11', '/usr/openwin/bin'],
                args=['-root'],
                errors='ignore'
            )
            if xwininfo.is_found():
                task = subtask_mod.Batch(xwininfo.get_cmdline())
                task.run()
                width = '???'
                for line in task.get_output():
                    if 'Width:' in line:
                        width = line.split()[-1]
                    elif 'Height:' in line:
                        Writer.output(
                            name='X-Windows Display',
                            value=display,
                            comment=f'{width}x{line.split()[-1]}',
                        )

    @classmethod
    def _xwindows(cls) -> None:
        display = os.environ.get('DISPLAY')
        if display:
            cls._xset()
            cls._xdisplay(display)

    @staticmethod
    def _software() -> None:
        software = Software()
        for file, version, comment in software.detect():
            Writer.output('Software', value=file+' '+version, comment=comment)

    def show_banner(self) -> None:
        """
        Show banner.
        """
        timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')
        print(f"\n{self._author} - System configuration detection tool")
        print(f"\n*** Detected at {timestamp} ***")

    def show_info(self) -> None:
        """
        Show information.
        """
        self._network_information()
        self._operating_system()
        self._processors()
        self._system_status()
        if self._system.has_devices():
            self._system.detect_devices()
        if self._system.has_loader():
            self._system.detect_loader()
        self._xwindows()
        self._software()


class OperatingSystem:
    """
    Operating system class
    """

    @staticmethod
    def detect_loader() -> None:
        """
        Detect loader
        """
        ldd = command_mod.Command('ldd', args=['/bin/sh'], errors='ignore')
        if ldd.is_found():
            task = subtask_mod.Batch(ldd.get_cmdline())
            task.run(pattern='libc.*=>')
            if task.has_output():
                try:
                    glibc = task.get_output()[0].split()[2]
                    version = file_mod.FileUtil.strings(
                        glibc, 'GNU C Library').split(
                            'version')[1].replace(',', ' ').split()[0]
                    if version.endswith('.'):
                        version = version[:-1]
                except IndexError:
                    pass
                else:
                    Writer.output(
                        name='GNU C library',
                        location=glibc,
                        value=version,
                    )
        for linker in sorted(glob.glob('/lib*/ld-*so*')):
            Writer.output(name='Dynamic linker', location=linker)

    def detect_devices(self) -> None:
        """
        Detect devices
        """

    @staticmethod
    def has_devices() -> bool:
        """
        Return False
        """
        return False

    @staticmethod
    def has_loader() -> bool:
        """
        Return False
        """
        return False

    @staticmethod
    def get_fqdn() -> str:
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        try:
            fqdn = (socket.getfqdn()).lower()
        except LookupError:
            return 'Unknown'
        if fqdn.count('.') < 2:
            return 'Unknown'
        if fqdn.endswith('.'):
            return fqdn
        return fqdn + '.'

    @classmethod
    def get_net_info(cls) -> dict:
        """
        Return network information dictionary.
        """
        info: dict = {}
        info['Net FQDN'] = cls.get_fqdn()
        info['Net IPvx Address'] = []
        info['Net IPvx DNS'] = []
        return info

    def get_os_info(self) -> dict:  # pylint: disable = no-self-use
        """
        Return operating system information dictionary.
        """
        info = {}
        info['OS Type'] = command_mod.Platform.get_system()
        info['OS Name'] = 'Unknown'
        info['OS Kernel'] = 'Unknown'
        info['OS Kernel X'] = ''
        info['OS Patch'] = 'Unknown'
        info['OS Patch X'] = ''
        info['OS Boot'] = 'Unknown'
        return info

    def get_cpu_info(self) -> dict:  # pylint: disable = no-self-use
        """
        Return CPU information dictionary.
        """
        info: dict = {}
        info['CPU Type'] = command_mod.Platform.get_arch()
        info['CPU Addressability'] = 'Unknown'
        info['CPU Addressability X'] = ''
        info['CPU Model'] = 'Unknown'
        info['CPU Sockets'] = 'Unknown'
        info['CPU Cores'] = 'Unknown'
        info['CPU Cores X'] = ''
        info['CPU Threads'] = 'Unknown'
        info['CPU Threads X'] = ''
        info['CPU Clock'] = 'Unknown'
        info['CPU Clocks'] = 'Unknown'
        info['CPU Cache'] = {}
        if command_mod.Platform.get_arch() == 'x86':
            info['CPU Type'] = 'x86'
        elif command_mod.Platform.get_arch() == 'x86_64':
            info['CPU Type'] = 'x86'
        return info

    def get_sys_info(self) -> dict:  # pylint: disable = no-self-use
        """
        Return system information dictionary.
        """
        info = {}
        info['System Platform'] = command_mod.Platform.get_platform()
        info['System Platform X'] = ''
        info['System Memory'] = 'Unknown'
        info['System Swap Space'] = 'Unknown'
        info['System Uptime'] = 'Unknown'
        info['System Load'] = 'Unknown'
        return info

    @staticmethod
    def _has_value(values: dict, word: str) -> bool:
        for value in values.values():
            if word in str(value[0]):
                return True
        return False

    @staticmethod
    def _isitset(values: dict, name: str) -> str:
        if name in values:
            return values[name][0]
        return 'Unknown'

    @staticmethod
    def factory() -> 'OperatingSystem':
        """
        Return OperatignSystem sub class
        """

        if os.name == 'nt':
            return WindowsSystem()

        osname = os.uname()[0]
        if osname == 'Darwin':
            return MacSystem()
        if osname == 'Linux':
            return LinuxSystem()

        return OperatingSystem()


class PosixSystem(OperatingSystem):
    """
    Posix system class
    """

    @staticmethod
    def _detect_battery() -> None:
        batteries = power_mod.Battery.factory()

        for battery in batteries:
            if battery.is_exist():
                model = (
                    f'{battery.get_oem()} {battery.get_name()} '
                    f'{battery.get_type()} ' f'{battery.get_capacity_max()}'
                    f'mAh/{battery.get_voltage()}mV'
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
                Writer.output(
                    name='Battery device',
                    device='/dev/???',
                    value=f'{battery.get_capacity()}mAh',
                    comment=f'{model} [{state}]',
                )

    def detect_devices(self) -> None:
        """
        Detect devices
        """
        self._detect_battery()

    @staticmethod
    def has_devices() -> bool:
        return True

    @classmethod
    def get_fqdn(cls) -> str:
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        ispattern = re.compile(r'\s*(domain|search)\s')
        try:
            with open(
                '/etc/resolv.conf',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        fqdn = (
                            f"{socket.gethostname().split('.')[0].lower()}."
                            f"{line.split()[1]}"
                        )
                        if fqdn.endswith('.'):
                            return fqdn
                        return fqdn + '.'
        except (IndexError, OSError):
            pass
        return super().get_fqdn()

    @classmethod
    def get_net_info(cls) -> dict:
        """
        Return network information dictionary.
        """
        info = super().get_net_info()
        ispattern = re.compile(r'\s*nameserver\s*\d')
        try:
            with open(
                '/etc/resolv.conf',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        info['Net IPvx DNS'].append(line.split()[1])
        except (IndexError, OSError):
            pass
        return info

    def get_os_info(self) -> dict:
        """
        Return operating system information dictionary.
        """
        info = super().get_os_info()
        info['OS Kernel'] = command_mod.Platform.get_kernel()
        info['OS Kernel X'] = os.uname()[3].replace('(', '').replace(')', '')
        return info

    def get_cpu_info(self) -> dict:
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()
        return info

    def get_sys_info(self) -> dict:
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()
        uptime = command_mod.Command('uptime', errors='ignore')
        if uptime.is_found():
            task = subtask_mod.Batch(uptime.get_cmdline())
            task.run()
            try:
                info['System Uptime'] = ','.join(task.get_output(
                    )[0].split(',')[:2]).split('up ')[1].strip()
                info['System Load'] = task.get_output(
                    )[0].split(': ')[-1]
            except (IndexError, OSError):
                pass
        return info


class LinuxSystem(PosixSystem):
    """
    Linux system class
    """

    def __init__(self) -> None:
        device = None
        self._devices: dict = {}
        lspci = command_mod.Command(
            'lspci',
            pathextra=['/sbin'],
            args=['-k'],
            errors='ignore'
        )
        modinfo = command_mod.Command(
            'modinfo',
            pathextra=['/sbin'],
            errors='ignore'
        )
        if lspci.is_found():
            task = subtask_mod.Batch(lspci.get_cmdline())
            task.run()
            if not task.has_output():
                lspci.set_args([])
                task = subtask_mod.Batch(lspci.get_cmdline())
                task.run()
            for line in task.get_output():
                if 'Kernel driver in use:' in line:
                    driver = line.split()[-1]
                    if modinfo.is_found():
                        task2 = subtask_mod.Batch(
                            modinfo.get_cmdline() + [driver])
                        task2.run(pattern='^(version|vermagic):')
                        if task2.has_output():
                            self._devices[device] = (
                                f'{driver} driver '
                                f'{task2.get_output()[0].split()[1]}'
                            )
                            continue
                elif not line.startswith('\t'):
                    device = line.replace('(', '').replace(')', '')
                    if 'VGA compatible controller: ' in line:
                        self._devices[device] = self._scan_vga(
                            line, device, modinfo)
                    else:
                        self._devices[device] = ''

    @staticmethod
    def _scan_vga(line: str, device: str, modinfo: command_mod.Command) -> str:
        device = ''
        if 'nvidia' in line.lower():
            try:
                with open(
                    '/proc/driver/nvidia/version',
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    for line2 in ifile:
                        if 'Kernel Module ' in line2:
                            name = line2.split('Kernel Module ')[1].split()[0]
                            device = f'nvidia driver {name}'
            except OSError:
                pass
        elif 'VirtualBox' in line and modinfo.is_found():
            task2 = subtask_mod.Batch(modinfo.get_cmdline() + ['vboxvideo'])
            task2.run(pattern='^(version|vermagic):')
            if task2.has_output():
                device = (
                    f'vboxvideo driver {task2.get_output()[0].split()[1]}'
                )

        return device

    @classmethod
    def _detect_audio(cls) -> None:
        info = {}
        ispattern = re.compile(r' ?\d+ ')
        try:
            with open(
                '/proc/asound/cards',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        try:
                            card = line.split()[0]
                            info[card] = line.split('-')[-1].strip()
                        except IndexError:
                            continue
        except OSError:
            pass

        for card, model in info.items():
            for file in sorted(glob.glob(
                    f'/proc/asound/card{card}/pcm*[cp]/info')):
                try:
                    with open(
                        file,
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
                        for line in ifile:
                            if line.startswith('name: '):
                                name = line.rstrip(
                                    '\r\n',
                                ).replace('name: ', '', 1)
                                name = f'{model} {name}'
                except (IndexError, OSError):
                    continue

                device = (
                    f"/dev/snd/pcmC{card}D"
                    f"{os.path.dirname(file).split('pcm')[-1]}"
                )
                if device.endswith('p'):
                    comment = 'SPK'
                else:
                    comment = 'MIC'
                Writer.output(
                    name='Audio device',
                    device=device,
                    value=name,
                    comment=comment,
                )

    @staticmethod
    def _detect_cd_proc_ide() -> None:
        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                with open(
                    os.path.join(directory, 'driver'),
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    for line in ifile:
                        if line.startswith('ide-cdrom '):
                            with open(
                                os.path.join(directory, 'model'),
                                encoding='utf-8',
                                errors='replace'
                            ) as ifile:
                                model = ifile.readline().strip()
                                Writer.output(
                                    name='CD device',
                                    device='/dev/'
                                    f'{os.path.basename(directory)}',
                                    value=model,
                                )
                                break
            except OSError:
                pass

    @staticmethod
    def _detect_cd_sys_scsi() -> None:
        for file in sorted(glob.glob('/sys/block/sr*/device')):  # New kernels
            try:
                identity = os.path.basename(os.readlink(file))
            except OSError:
                continue
            try:
                if os.path.isdir(f'/sys/bus/scsi/devices/{identity}'):
                    with open(
                        os.path.join(
                            '/sys/bus/scsi/devices',
                            identity,
                            'vendor',
                        ),
                        encoding='utf-8',
                        errors='replace'
                    ) as ifile:
                        model = ifile.readline().strip()
                    with open(
                        os.path.join(
                            '/sys/bus/scsi/devices',
                            identity,
                            'model',
                        ),
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
                        model += f' {ifile.readline().strip()}'
            except OSError:
                model = '???'
            device = f'/dev/{os.path.basename(os.path.dirname(file))}'
            Writer.output(name='CD device', device=device, value=model)

    @staticmethod
    def _detect_cd_proc_scsi() -> None:
        model = '???'
        unit = 0
        isjunk = re.compile('.*Vendor: | *Model:| *Rev: .*')
        try:
            with open(
                '/proc/scsi/scsi',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if 'Vendor: ' in line and 'Model: ' in line:
                        model = isjunk.sub('', line.rstrip('\r\n'))
                    elif 'Type:' in line and 'CD-ROM' in line:
                        if os.path.exists(f'/dev/sr{unit}'):
                            device = f'/dev/sr{unit}'
                        else:
                            device = f'/dev/scd{unit}'
                        Writer.output(
                            name='CD device',
                            device=device,
                            value=model,
                        )
                        model = '???'
                        unit += 1
        except OSError:
            pass

    @classmethod
    def _detect_cd(cls) -> None:
        cls._detect_cd_proc_ide()

        if os.path.isdir('/sys/bus/scsi/devices'):
            cls._detect_cd_sys_scsi()
        else:
            cls._detect_cd_proc_scsi()

    @staticmethod
    def _get_disk_info() -> dict:
        info: dict = {}
        info['partitions'] = []
        info['swaps'] = []
        try:
            with open(
                '/proc/partitions',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    info['partitions'].append(line.rstrip('\r\n'))
        except OSError:
            pass
        try:
            with open(
                '/proc/swaps',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if line.startswith('/dev/'):
                        info['swaps'].append(line.split()[0])
        except OSError:
            pass
        return info

    @staticmethod
    def _scan_mounts(info: dict) -> None:
        info['mounts'] = {}
        try:
            with open(
                '/proc/mounts',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    try:
                        device, mount_point, mount_type = line.split()[:3]
                        mount_info = (mount_point, mount_type)
                        if device in info['mounts']:
                            info['mounts'][device].append(mount_info)
                        else:
                            info['mounts'][device] = [mount_info]
                    except IndexError:
                        pass
        except OSError:
            pass

        try:
            with open(
                '/proc/swaps',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if line.startswith('/dev/'):
                        info['swaps'].append(line.split()[0])
        except OSError:
            pass

    @staticmethod
    def _detect_ide_partition(
        info: dict,
        model: str,
        hdx: str,
        partition: str,
    ) -> None:
        if partition.endswith(hdx) or hdx + ' ' in partition:
            try:
                size = partition.split()[2]
            except IndexError:
                size = '???'
            Writer.output(
                name='Disk device',
                device=f'/dev/{hdx}',
                value=size + ' KB',
                comment=model,
            )
        elif hdx in partition:
            size, hdxn = partition.split()[2:4]
            device = f'/dev/{hdxn}'
            comment = ''
            if device in info['swaps']:
                comment = 'swap'
            elif device in info['mounts']:
                for mount_point, mount_type in info[
                        'mounts'][device]:
                    comment = f'{mount_type} on {mount_point}'
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=size + ' KB',
                        comment=comment,
                    )
                return
            else:
                comment = ''
            Writer.output(
                name='Disk device',
                device=device,
                value=size + ' KB',
                comment=comment,
            )

    @classmethod
    def _detect_disk_ide(cls, info: dict, directory: str) -> None:
        with open(
            os.path.join(directory, 'driver'),
            encoding='utf-8',
            errors='replace'
        ) as ifile:
            for line in ifile:
                if line.startswith('ide-disk '):
                    file = os.path.join(directory, 'model')
                    with open(
                        file,
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile2:
                        model = ifile2.readline().rstrip('\r\n')
                    hdx = os.path.basename(directory)
                    for partition in info['partitions']:
                        cls._detect_ide_partition(info, model, hdx, partition)

    @staticmethod
    def _get_disk_sys_scsi_model(file: str) -> str:
        try:
            identity = os.path.basename(os.readlink(file))
        except OSError:
            return None

        try:
            if os.path.isdir(f'/sys/bus/scsi/devices/{identity}'):
                with open(
                    os.path.join(
                        '/sys/bus/scsi/devices',
                        identity,
                        'vendor',
                    ),
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    model = ifile.readline().strip()
                with open(
                    os.path.join(
                        '/sys/bus/scsi/devices',
                        identity,
                        'model',
                    ),
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    model += f' {ifile.readline().strip()}'
        except OSError:
            model = '???'

        return model

    @classmethod
    def _detect_disk_sys_scsi(cls, info: dict, file: str) -> None:
        model = cls._get_disk_sys_scsi_model(file)

        sdx = os.path.basename(os.path.dirname(file))
        for partition in info['partitions']:
            if partition.endswith(sdx) or sdx + ' ' in partition:
                try:
                    size = partition.split()[2]
                except IndexError:
                    size = '???'
                device = f'/dev/{sdx}'
                if device in info['mounts']:
                    for mount_point, mount_type in info['mounts'][device]:
                        comment = f'{mount_type} on {mount_point}'
                        Writer.output(
                            name='Disk device',
                            device=device,
                            value=f'{size} KB',
                            comment=f'{comment}, {model}',
                        )
                    continue
                Writer.output(
                    name='Disk device',
                    device=f'/dev/{sdx}',
                    value=f'{size} KB',
                    comment=model,
                )
            elif sdx in partition:
                size, sdxn = partition.split()[2:4]
                device = f'/dev/{sdxn}'
                if device in info['swaps']:
                    comment = 'swap'
                elif device in info['mounts']:
                    for mount_point, mount_type in info['mounts'][device]:
                        comment = f'{mount_type} on {mount_point}'
                        Writer.output(
                            name='Disk device',
                            device=device,
                            value=f'{size} KB',
                            comment=comment,
                        )
                    continue
                elif glob.glob(f'/sys/class/block/dm-*/slaves/{sdxn}'):
                    comment = 'devicemapper'
                else:
                    comment = ''
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=f'{size} KB',
                    comment=comment,
                )

    @staticmethod
    def _detect_disk_proc_scsi_part(info: dict, unit: int, model: str) -> None:
        sdx = f'sd{chr(97)}{unit}'
        if os.path.exists(f'/dev/{sdx}'):
            for partition in info['partitions']:
                if partition.endswith(sdx) or '{sdx} ' in partition:
                    try:
                        size = partition.split()[2]
                    except IndexError:
                        size = '???'
                    Writer.output(
                        name='Disk device',
                        device=f'/dev/{sdx}',
                        value=f'{size} KB',
                        comment=model,
                    )
                elif sdx in partition:
                    size, sdxn = partition.split()[2:4]
                    device = f'/dev/{sdxn}'
                    if device in info['swaps']:
                        comment = 'swap'
                    elif device in info['mounts']:
                        for mount_point, mount_type in info['mounts'][device]:
                            comment = f'{mount_type} on {mount_point}'
                            Writer.output(
                                name='Disk device',
                                device=device,
                                value=f'{size} KB',
                                comment=comment,
                            )
                        continue
                    else:
                        comment = ''
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=f'{size} KB',
                        comment=comment,
                    )

    @classmethod
    def _detect_disk_proc_scsi(cls, info: dict) -> None:
        model = '???'
        unit = 0
        isjunk = re.compile('.*Vendor: | *Model:| *Rev: .*')
        try:
            with open(
                '/proc/scsi/scsi',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if 'Vendor: ' in line and 'Model: ' in line:
                        model = isjunk.sub('', line.rstrip('\r\n'))
                    elif 'Type:' in line and 'Direct-Access' in line:
                        cls._detect_disk_proc_scsi_part(info, unit, model)
                        model = '???'
                        unit += 1
        except OSError:
            pass

    @staticmethod
    def _detect_mapped_disks(info: dict) -> None:
        for directory in glob.glob('/sys/class/block/dm-*'):
            file = os.path.join(directory, 'dm/name')
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    device = f'/dev/mapper/{ifile.readline().strip()}'
            except OSError:
                device = '???'
            mount_info = info['mounts'].get(device, ())

            slaves = '+'.join([os.path.basename(file) for file in glob.glob(
                os.path.join(directory, 'slaves', '*')
            )])

            file = os.path.join(directory, 'size')
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    size = f'{int(ifile.readline()) >> 1} KB'
            except (OSError, ValueError):
                size = '??? KB'

            file = os.path.join(directory, 'dm', 'uuid')
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    slaves = f"{ifile.readline().split('-')[0]}:{slaves}"
            except (OSError, ValueError):
                slaves = f'???:{slaves}'

            if f'/dev/{os.path.basename(directory)}' in info['swaps']:
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=size,
                    comment=f'swap, {slaves}',
                )
            else:
                for mount_point, mount_type in mount_info:
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=size,
                        comment=f'{mount_type} on {mount_point}, {slaves}',
                    )

    @staticmethod
    def _detect_remote_disks(info: dict) -> None:
        command = command_mod.Command(
            'df',
            args=['-k'],
            errors='ignore'
        )
        for device in sorted(info['mounts']):
            if ':' in device:
                mount_point, mount_type = info['mounts'][device][0]
                size = '??? KB'
                if command.is_found():
                    command.set_args([mount_point])
                    thread = CommandThread(command)
                    thread.start()
                    end_time = time.time() + 1  # One second delay limit
                    while thread.is_alive():
                        if time.time() > end_time:
                            thread.kill()
                            break
                    try:
                        size = thread.get_output().split()[-5] + ' KB'
                    except IndexError:
                        pass
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=size,
                    comment=f'{mount_type} on {mount_point}',
                )

    @classmethod
    def _detect_disk(cls) -> None:
        info = cls._get_disk_info()
        cls._scan_mounts(info)

        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                cls._detect_disk_ide(info, directory)
            except OSError:
                pass

        if glob.glob('/sys/bus/scsi/devices/*'):  # New kernels has devices
            for file in sorted(glob.glob('/sys/block/*d[a-z]*/device')):
                cls._detect_disk_sys_scsi(info, file)
        else:
            cls._detect_disk_proc_scsi(info)
        cls._detect_mapped_disks(info)
        cls._detect_remote_disks(info)

    def _detect_graphics(self) -> None:
        if os.path.isdir('/dev/dri'):
            gpus = glob.glob('/sys/bus/pci/devices/*/drm/card*')
        else:
            gpus = glob.glob('/sys/bus/pci/devices/*/graphics/fb*')
        if gpus:
            for gpu in sorted(gpus):
                if os.path.isdir('/dev/dri'):
                    device = os.path.join('/dev/dri', os.path.basename(gpu))
                else:
                    device = os.path.join('/dev', os.path.basename(gpu))
                if os.path.exists(device):
                    pci_id = gpu.split('/')[-3].split(':', 1)[-1]
                    model, comment = self._match_pci(pci_id)
                    Writer.output(
                        name='Graphics device',
                        device=device,
                        value=model,
                        comment=comment,
                    )
        else:
            xrandr = command_mod.Command('xrandr', errors='ignore')
            if xrandr.is_found():
                task = subtask_mod.Batch(xrandr.get_cmdline())
                task.run()
                if task.has_output():
                    for key, value in self._devices.items():
                        if 'VGA compatible controller:' in key:
                            model = key.split(': ', 1)[-1]
                            comment = value
                            Writer.output(
                                name='Graphics device',
                                device='/dev/???',
                                value=model,
                                comment=comment,
                            )

    @staticmethod
    def _detect_input() -> None:
        info = {}
        model = '???'
        try:
            with open(
                '/proc/bus/input/devices',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if line.startswith('N: Name="'):
                        model = line.split('"')[1]
                    elif line.startswith('H: Handlers='):
                        event = line.split('event')[-1].split()[0]
                        info[f'/dev/input/event{event}'] = model
        except OSError:
            pass
        devices = [
            os.path.join('/dev/input', os.path.basename(os.readlink(file)))
            for file in glob.glob('/dev/input/by-path/*')
            if 'event' in file
        ]
        for device in sorted(devices):
            if os.path.exists(device):
                Writer.output(
                    name='Input device',
                    device=device,
                    value=info[device],
                )

    def _detect_network(self) -> None:
        networks = [
            network.replace('net:', 'net/')
            for network in (
                glob.glob('/sys/bus/pci/devices/*/net/*') +
                glob.glob('/sys/bus/pci/devices/*/net:*')
            )
        ]
        for network in sorted(networks):
            device = f'net/{os.path.basename(network)}'
            pci_id = network.split('/')[-3].split(':', 1)[-1]
            model, comment = self._match_pci(pci_id)
            model = model.replace(
                'Semiconductor ', '').replace('Co., ', '').replace(
                    'Ltd. ', '').replace('PCI Express ', '')
            Writer.output(
                name='Network device',
                device=device,
                value=model,
                comment=comment,
            )

    @staticmethod
    def _detect_video() -> None:
        for directory in sorted(glob.glob('/sys/class/video4linux/*')):
            device = os.path.basename(directory)
            try:
                with open(
                    os.path.join(directory, 'name'),
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    Writer.output(
                        name='Video device',
                        device=f'/dev/{device}',
                        value=ifile.readline().rstrip('\r\n'),
                    )
                    continue
            except OSError:
                pass
            Writer.output(
                name='Video device',
                device=f'/dev/{device}', value='???',
            )

    @staticmethod
    def _detect_zram() -> None:
        zramctl = command_mod.Command(
            'zramctl',
            pathextra=['/sbin'],
            args=['--noheadings', '--bytes'],
            errors='ignore',
        )
        if zramctl.is_found():
            task = subtask_mod.Batch(zramctl.get_cmdline())
            task.run()
            for line in task.get_output():
                device, algorithm, size, data, compress, *_ = line.split()
                Writer.output(
                    name='ZRAM device',
                    device=device,
                    value=f'{int(int(size) / 1024 + 0.5)} KB',
                    comment=(
                        f'{int(int(data) / 1024 + 0.5)} KB data, '
                        f'{int(int(compress) / 1024 + 0.5)} KB '
                        f'{algorithm}, '
                        f'{int(data) / int(compress):3.1f}X'
                    )
                )

    def _match_pci(self, pci_id: str) -> Tuple[str, str]:
        model = '???'
        comment = ''
        for key, value in self._devices.items():
            if key.startswith(pci_id):
                model = key.split(': ', 1)[-1]
                comment = value
                break
        return model, comment

    def detect_devices(self) -> None:
        """
        Detect devices
        """
        self._detect_audio()
        self._detect_battery()
        self._detect_cd()
        self._detect_disk()
        self._detect_graphics()
        self._detect_input()
        self._detect_network()
        self._detect_video()
        self._detect_zram()

    @staticmethod
    def has_loader() -> bool:
        """
        Return True
        """
        return True

    @classmethod
    def get_net_info(cls) -> dict:
        """
        Return network information dictionary.
        """
        info = super().get_net_info()
        env = {}
        env['LANG'] = os.environ.get('LANG', 'en_US')
        command = command_mod.Command(
            'ip',
            args=['address'],
            pathextra=['bin', '/sbin'],
            errors='ignore'
        )
        if not command.is_found():
            command = command_mod.CommandFile('/sbin/ifconfig', args=['-a'])
        task = subtask_mod.Batch(command.get_cmdline())
        task.run(env=env, pattern='^ *inet6? ')
        isjunk = re.compile('^ *inet6? (addr[a-z]*[: ])?')
        for line in task.get_output():
            info['Net IPvx Address'].append(isjunk.sub(' ', line).split()[0])
        return info

    @staticmethod
    def _scan_etc_release() -> dict:
        info = {}

        if os.path.isfile('/etc/redhat-release'):
            try:
                with open(
                    '/etc/redhat-release',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    info['OS Name'] = ifile.readline().rstrip('\r\n')
            except OSError:
                pass
        elif os.path.isfile('/etc/SuSE-release'):
            try:
                with open(
                    '/etc/SuSE-release',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    info['OS Name'] = ifile.readline().rstrip('\r\n')
                    for line in ifile:
                        if 'PATCHLEVEL' in line:
                            try:
                                info['OS Patch'] = line.split()[-1]
                                break
                            except IndexError:
                                pass
            except OSError:
                info['OS Name'] = 'Unknown'
        elif os.path.isfile('/etc/alpine-release'):
            try:
                with open(
                    '/etc/alpine-release',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    name = ifile.readline().rstrip('\\r\\n')
                    info['OS Name'] = f'Alpine {name}'
            except OSError:
                pass

        return info

    @staticmethod
    def _scan_etc_lsb_release() -> dict:
        info = {}

        if os.path.isfile('/etc/lsb-release'):
            try:
                with open(
                    '/etc/lsb-release',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    lines = []
                    for line in ifile:
                        lines.append(line.rstrip('\r\n'))
            except OSError:
                pass
            else:
                if lines and lines[-1].startswith('DISTRIB_DESCRIPTION='):
                    info['OS Name'] = lines[-1].split('=')[1].replace('"', '')
                else:
                    identity = None
                    for line in lines:
                        if line.startswith('DISTRIB_ID='):
                            identity = line.split('=')[1]
                        elif line.startswith('DISTRIB_RELEASE=') and identity:
                            info['OS Name'] = (
                                f"{identity} {line.split('=')[1]}"
                            )
                            break

        return info

    @staticmethod
    def _scan_etc_version() -> dict:
        info = {}

        if os.path.isfile('/etc/kanotix-version'):
            try:
                with open(
                    '/etc/kanotix-version',
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    name = ifile.readline().rstrip('\r\n').split()[1]
                    info['OS Name'] = f'Kanotix {name}'
            except (IndexError, OSError):
                pass
        elif os.path.isfile('/etc/knoppix-version'):
            try:
                with open(
                    '/etc/knoppix-version',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    name = ifile.readline().rstrip('\r\n').split()[0]
                    info['OS Name'] = f'Knoppix {name}'
            except (IndexError, OSError):
                pass
        elif os.path.isfile('/etc/debian_version'):
            try:
                with open(
                    '/etc/debian_version',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    name = ifile.readline().rstrip(
                        '\r\n',
                    ).split('=')[-1].replace("'", '')
                    info['OS Name'] = f'Debian {name}'
            except OSError:
                pass
        elif os.path.isfile('/etc/DISTRO_SPECS'):
            try:
                identity = None
                with open(
                    '/etc/DISTRO_SPECS',
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    for line in ifile:
                        if line.startswith('DISTRO_NAME'):
                            identity = line.rstrip(
                                '\r\n').split('=')[1].replace('"', '')
                        elif line.startswith('DISTRO_VERSION') and identity:
                            name = line.rstrip('\r\n').split('=')[1]
                            info['OS Name'] = f'{identity} {name}'
                            break
            except (IndexError, OSError):
                pass

        return info

    @staticmethod
    def _scan_dpkg_version() -> dict:
        info = {}

        dpkg = command_mod.Command('dpkg', args=['--list'], errors='ignore')
        if dpkg.is_found():
            task = subtask_mod.Batch(dpkg.get_cmdline())
            task.run()
            for line in task.get_output():
                try:
                    package = line.split()[1]
                    if package == 'knoppix-g':
                        info['OS Name'] = (
                            f"Knoppix {line.split()[2].split('-')[0]}"
                        )
                        return info
                    if package == 'mepis-auto':
                        info['OS Name'] = f'MEPIS {line.split()[2]}'
                        return info
                    if ' kernel ' in line and 'MEPIS' in line:
                        isjunk = re.compile('MEPIS.')
                        info['OS Name'] = (
                            f"MEPIS {isjunk.sub('', line.split()[2])}"
                        )
                        return info
                except IndexError:
                    pass
            for line in task.get_output():
                try:
                    package = line.split()[1]
                    if package == 'base-files':
                        info['OS Name'] = f'Debian {line.split()[2]}'
                        return info
                except IndexError:
                    pass
            return info

        return info

    @staticmethod
    def _scan_os_release() -> dict:
        info = {}

        try:
            with open(
                '/etc/os-release',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if line.startswith('PRETTY_NAME="'):
                        info['OS Name'] = line.split('"')[1].split('(')[0]
                        break
        except OSError:
            pass

        return info

    @staticmethod
    def _scan_clear_version() -> dict:
        info = {}

        try:
            with open(
                '/usr/share/clear/version',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                info['OS Name'] = f'Clear Linux {ifile.readline().strip()}'
        except OSError:
            pass

        return info

    @staticmethod
    def _scan_systemd() -> dict:
        info = {}

        systemd_analyze = command_mod.Command(
            'systemd-analyze',
            errors='ignore'
        )
        if systemd_analyze.is_found():
            task = subtask_mod.Batch(systemd_analyze.get_cmdline())
            task.run(pattern='^Startup finished in ')
            if task.has_output():
                info['OS Boot'] = task.get_output()[0].replace(
                    'Startup finished in ',
                    '',
                )

        return info

    def get_os_info(self) -> dict:
        """
        Return operating system information dictionary.
        """
        info = super().get_os_info()

        for scan_method in (
                self._scan_etc_release,
                self._scan_etc_lsb_release,
                self._scan_etc_version,
                self._scan_dpkg_version,
                self._scan_os_release,
                self._scan_clear_version,
        ):
            info.update(scan_method())
            if info['OS Name'] != 'Unknown':
                break
        info.update(self._scan_systemd())
        return info

    @staticmethod
    def _scan_frequency(info: dict, lines: List[str]) -> None:
        try:
            with open(
                '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                info['CPU Clock'] = str(int(
                    int(ifile.readline().rstrip('\r\n')) / 1000 + 0.5))
        except (OSError, ValueError):
            for line in lines:
                if line.startswith('cpu MHz'):
                    try:
                        info['CPU Clock'] = str(int(
                            float(line.split(': ')[1]) + 0.5))
                    except (IndexError, ValueError):
                        pass
                    break
            if info['CPU Clock'] == 'Unknown':
                for line in lines:
                    if line.startswith('clock'):
                        try:
                            info['CPU Clock'] = str(int(
                                float(line.split(': ')[1]) + 0.5))
                        except (IndexError, ValueError):
                            pass
                        break

        found = []
        try:
            with open(
                '/sys/devices/system/cpu/cpu0/cpufreq/'
                'scaling_available_frequencies',
                encoding='utf-8',
                errors='replace'
            ) as ifile:
                for clock in ifile.readline().rstrip('\r\n').split():
                    found.append(str(int(int(clock) / 1000 + 0.5)))
                if found:
                    info['CPU Clocks'] = ' '.join(found)
        except (OSError, ValueError):
            try:
                with open(
                    '/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq',
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    info['CPU Clocks'] = str(int(
                        int(ifile.readline()) / 1000 + 0.5))
                with open(
                    '/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq',
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    info['CPU Clocks'] += (
                        f' {int(int(ifile.readline()) / 1000 + 0.5)}'
                    )
            except (OSError, ValueError):
                info['CPU Clocks'] = 'Unknown'

    @staticmethod
    def _get_proc_cpuinfo() -> List[str]:
        lines = []
        try:
            with open(
                '/proc/cpuinfo',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except OSError:
            pass

        return lines

    @staticmethod
    def _scan_cpu_model(info: dict, lines: List[str]) -> None:
        isspace = re.compile(r'\s+')

        try:
            if command_mod.Platform.get_arch() == 'Power':
                for line in lines:
                    if line.startswith('cpu'):
                        name = isspace.sub(
                            ' ',
                            line.split(': ')[1].split(' ')[0].strip(),
                        )
                        info['CPU Model'] = f'PowerPC_{name}'
                        break
            if info['CPU Model'] == 'Unknown':
                for line in lines:
                    if line.startswith('model name'):
                        info['CPU Model'] = isspace.sub(
                            ' ', line.split(': ')[1].strip())
                        break
            if command_mod.Platform.get_arch() == 'x86_64':
                for line in lines:
                    if line.startswith('address size'):
                        info['CPU Addressability X'] = line.split(
                            ':')[1].split()[0] + 'bit physical'
        except (IndexError, OSError):
            pass

    @staticmethod
    def _get_cpu_threads(lines: List[str]) -> int:
        try:
            threads = len(glob.glob('/sys/devices/system/cpu/cpu[0-9]*'))
        except (IndexError, ValueError):
            threads = 0
        if not threads:
            for line in lines:
                if line.startswith('processor'):
                    threads += 1

        return threads

    @staticmethod
    def _get_cpu_physical_packages() -> List[str]:
        found = []

        for file in glob.glob(
                '/sys/devices/system/cpu/cpu[0-9]*/'
                'topology/physical_package_id'
        ):
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    line = ifile.readline().rstrip('\r\n')
                    if line not in found:
                        found.append(line)
            except OSError:
                pass

        return found

    def _get_cpu_sockets(self, lines: List[str], threads: int) -> int:
        found = self._get_cpu_physical_packages()
        if found:
            sockets = len(found)
        else:
            for line in lines:
                if line.startswith('physical id'):
                    if line not in found:
                        found.append(line)
            if found:
                sockets = len(found)
            else:
                sockets = threads
                for line in lines:
                    if line.startswith('siblings'):
                        try:
                            sockets = int(threads / int(line.split()[2]))
                        except (IndexError, ValueError):
                            pass
                        break
        return sockets

    @staticmethod
    def _get_cpu_cores(
        info: dict,
        lines: List[str],
        sockets: int,
        threads: int,
    ) -> int:
        try:
            with open(
                '/sys/devices/system/cpu/cpu0/topology/thread_siblings_list',
                encoding='utf-8',
                errors='replace'
            ) as ifile:
                cpu_cores = int(threads/(int(
                    ifile.readline().rstrip('\r\n').split('-')[-1]) + 1))
        except (OSError, ValueError):
            cores_per_socket = None
            if 'Dual Core' in info['CPU Model']:
                cores_per_socket = 2
            elif 'Quad-Core' in info['CPU Model']:
                cores_per_socket = 4
            else:
                for line in lines:
                    if line.startswith('cpu cores'):
                        try:
                            cores_per_socket = int(line.split()[3])
                            if cores_per_socket == 1:
                                cores_per_socket = None
                        except (IndexError, ValueError):
                            pass
                        break
            if cores_per_socket:
                cpu_cores = sockets * cores_per_socket
            else:
                cpu_cores = sockets

        return cpu_cores

    @staticmethod
    def _scan_cache(info: dict, lines: List[str]) -> None:
        for cache in sorted(glob.glob(
                '/sys/devices/system/cpu/cpu0/cache/index*')):
            try:
                with open(
                    os.path.join(cache, 'level'),
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    level = ifile.readline().rstrip('\r\n')
                with open(
                    os.path.join(cache, 'type'),
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    type_ = ifile.readline().rstrip('\r\n')
                if type_ == 'Data':
                    level += 'd'
                elif type_ == 'Instruction':
                    level += 'i'
                with open(
                    os.path.join(cache, 'size'),
                    encoding='utf-8',
                    errors='replace'
                ) as ifile:
                    info['CPU Cache'][level] = str(int(
                        ifile.readline().rstrip('\r\nK')))
            except (OSError, ValueError):
                pass
        if not info['CPU Cache']:
            for line in lines:
                if line.startswith('cache size'):
                    try:
                        info['CPU Cache']['?'] = str(int(
                            float(line.split()[3])))
                    except (IndexError, ValueError):
                        pass
                    break

    def get_cpu_info(self) -> dict:
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()

        if info['CPU Addressability'] == 'Unknown':
            if command_mod.Platform.get_arch().endswith('64'):
                info['CPU Addressability'] = '64bit'
            else:
                info['CPU Addressability'] = '32bit'

        lines = self._get_proc_cpuinfo()
        self._scan_cpu_model(info, lines)
        threads = self._get_cpu_threads(lines)
        virtual_machine = self._get_virtual_machine()
        container = self._get_container()
        if virtual_machine:
            info['CPU Cores'] = str(threads)
            if container:
                info['CPU Cores X'] = (
                    f'{container} container, {virtual_machine} VM'
                )
            else:
                info['CPU Cores X'] = virtual_machine + ' VM'
            info['CPU Threads'] = info['CPU Cores']
            info['CPU Threads X'] = info['CPU Cores X']
        else:
            sockets = self._get_cpu_sockets(lines, threads)
            cpu_cores = self._get_cpu_cores(info, lines, sockets, threads)
            info['CPU Sockets'] = str(sockets)
            info['CPU Cores'] = str(cpu_cores)
            if container:
                info['CPU Cores X'] = container + ' container'
            info['CPU Threads'] = str(threads)

        self._scan_frequency(info, lines)
        self._scan_cache(info, lines)

        return info

    def get_sys_info(self) -> dict:
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()
        try:
            with open(
                '/proc/meminfo',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                try:
                    for line in ifile:
                        if line.startswith('MemTotal:'):
                            info['System Memory'] = str(int(
                                float(line.split()[1]) / 1024 + 0.5))
                        elif line.startswith('SwapTotal:'):
                            info['System Swap Space'] = str(int(
                                float(line.split()[1]) / 1024 + 0.5))
                except (IndexError, ValueError):
                    pass
        except OSError:
            pass
        return info

    @staticmethod
    def _get_container() -> str:
        name = None
        try:
            with open(
                '/proc/1/cgroup',
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                for line in ifile:
                    if '/docker/' in line or '/docker-' in line:
                        name = f"Docker {line.rsplit('/', 1)[1][:12]}"
                        break
                    if '/lxc/' in line:
                        name = 'LXC'
                        break
        except OSError:
            pass
        return name

    @staticmethod
    def _check_virtual_machine(data: str, mapping: dict) -> str:
        for vendor, text in mapping.items():
            if text in data:
                return vendor
        return ''

    def _get_virtual_machine(self) -> str:
        mappings = {
            'devices': {
                'VirtualBox': 'VirtualBox',
                'VMware': 'vmware',
                'Xen': ' Xen ',
            },
            'scsi': {
                'VirtualBox': 'VBOX ',
                'VMware': 'vmware',
            },
            'lsmod': {
                'Hyper-V': 'hv_',
                'VirtualBox': 'vboxguest',
                'VMware': 'vmw_',
                'Xen': 'xen_blkfront',
            },
        }
        name = None

        if os.path.isdir('/proc/xen'):
            name = 'Xen'
        elif not name:
            name = self._check_virtual_machine(
                ' '.join(self._devices),
                mappings['devices']
            )

        if not name:
            for file in (
                    glob.glob('/sys/bus/scsi/devices/*/model') +
                    ['/proc/scsi/scsi'] +
                    glob.glob('/proc/ide/hd?/model')
            ):
                try:
                    with open(
                        file,
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
                        name = self._check_virtual_machine(
                            ' '.join(ifile.readlines()),
                            mappings['scsi']
                        )
                except OSError:
                    pass

        if not name:
            lsmod = command_mod.Command(
                'lsmod',
                pathextra=['/sbin'],
                errors='ignore'
            )
            if lsmod.is_found():
                task = subtask_mod.Batch(lsmod.get_cmdline())
                task.run()
                name = self._check_virtual_machine(
                    ' '.join(task.get_output()),
                    mappings['lsmod']
                )
        return name


class MacSystem(PosixSystem):
    """
    Mac system class
    """

    def __init__(self) -> None:
        sysctl = command_mod.CommandFile('/usr/sbin/sysctl', args=['-a'])
        task = subtask_mod.Batch(sysctl.get_cmdline())
        task.run()

        # ' = ' is used in older versions of MacOS
        self._kernel_settings = [
            x.replace(' = ', ': ', 1) for x in task.get_output()]

    @staticmethod
    def _detect_disk() -> None:
        mount = command_mod.Command('mount', errors='ignore')
        if mount.is_found():
            task = subtask_mod.Batch(mount.get_cmdline())
            task.run(pattern='/dev/|:')
            for line in sorted(task.get_output()):
                try:
                    device, _, directory, type_ = line.replace(
                        '(', '').replace(',', '').split()[:4]
                except IndexError:
                    continue
                command = command_mod.Command(
                    'df',
                    args=['-k', directory],
                    errors='ignore'
                )
                task = subtask_mod.Batch(command.get_cmdline())
                task.run(pattern=f'^{device} .* ')
                for line2 in task.get_output():
                    size = line2.split()[1]
                    break
                else:
                    size = '???'
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=f'{size} KB',
                    comment=f'{type_} on {directory}',
                )

    def detect_devices(self) -> None:
        """
        Detect devices
        """
        self._detect_battery()
        self._detect_disk()

    @classmethod
    def get_net_info(cls) -> dict:
        """
        Return network information dictionary.
        """
        info = super().get_net_info()
        ifconfig = command_mod.CommandFile('/sbin/ifconfig', args=['-a'])
        task = subtask_mod.Batch(ifconfig.get_cmdline())
        task.run(pattern='inet[6]? ')
        isjunk = re.compile('.*inet[6]? |[% ].*')
        addresses = [isjunk.sub('', line) for line in task.get_output()]
        info['Net IPvx Address'] = list(dict.fromkeys(addresses))

        return info

    def get_os_info(self) -> dict:
        """
        Return operating system information dictionary.
        """
        info = super().get_os_info()
        system_profiler = command_mod.CommandFile(
            '/usr/sbin/system_profiler', args=['SPSoftwareDataType'])
        task = subtask_mod.Batch(system_profiler.get_cmdline())
        task.run(pattern='System Version: ')
        if task.has_output():
            info['OS Name'] = task.get_output(
                )[0].split(': ', 1)[1].split(' (')[0]
        return info

    def _get_cpu_socket_info(self) -> dict:
        for line in self._kernel_settings:
            if line.startswith('machdep.cpu.thread_count: '):
                threads = int(line.split(': ', 1)[1])
                break
        for line in self._kernel_settings:
            if line.startswith('machdep.cpu.core_count: '):
                cores = int(line.split(': ', 1)[1])
                break
        for line in self._kernel_settings:
            if line.startswith('machdep.cpu.cores_per_package: '):
                cores_per_package = min(int(line.split(': ', 1)[1]), cores)
                break
        else:
            cores_per_package = cores
        info = {}
        info['CPU Sockets'] = str(int(cores/cores_per_package))
        info['CPU Cores'] = str(cores)
        info['CPU Threads'] = str(threads)
        return info

    def get_cpu_info(self) -> dict:
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()

        for line in self._kernel_settings:
            if line == 'hw.cpu64bit_capable: 1':
                info['CPU Addressability'] = '64bit'
                break
        else:
            info['CPU Addressability'] = '32bit'
        for line in self._kernel_settings:
            if line.startswith('machdep.cpu.brand_string: '):
                info['CPU Model'] = line.split(': ', 1)[1]
                break

        info.update(self._get_cpu_socket_info())

        for line in self._kernel_settings:
            if line.startswith('hw.cpufrequency: '):
                info['CPU Clock'] = str(int(
                    float(line.split(': ', 1)[1])/1000000 + 0.5))
                break

        for line in self._kernel_settings:
            if line.startswith('hw.l') and 'cachesize: ' in line:
                info['CPU Cache'][line[4:].split('cachesize:')[0]] = (
                    f"{int(int(line.split(': ', 1)[1]) / 1024)}"
                )

        return info

    def get_sys_info(self) -> dict:
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()
        for line in self._kernel_settings:
            if line.startswith('hw.memsize: '):
                info['System Memory'] = str(int(
                    int(line.split(': ', 1)[1])/1048576 + 0.5))
                break
        for line in self._kernel_settings:
            if line.startswith('vm.swapusage: '):
                info['System Swap Space'] = line.split()[2].split('.')[0]
                break

        return info


class WindowsSystem(OperatingSystem):
    """
    Windows system class
    """

    def __init__(self) -> None:
        pathextra = []
        if 'WINDIR' in os.environ:
            pathextra.append(os.path.join(os.environ['WINDIR'], 'system32'))
        # Except for WIndows XP Home
        self._systeminfo = command_mod.Command(
            'systeminfo',
            pathextra=pathextra,
            errors='ignore'
        )

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _get_ipconfig() -> command_mod.Command:
        pathextra = []
        if 'WINDIR' in os.environ:
            pathextra.append(os.path.join(os.environ['WINDIR'], 'system32'))
        command = command_mod.Command(
            'ipconfig',
            pathextra=pathextra,
            errors='stop'
        )
        command.set_args(['-all'])
        return command

    @classmethod
    def get_fqdn(cls) -> str:
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        task = subtask_mod.Batch(cls._get_ipconfig().get_cmdline())
        task.run()
        for line in task.get_output('Connection-specific DNS Suffix'):
            fqdn = (
                f"{socket.gethostname().split('.')[0].lower()}."
                f"{line.split()[-1]}"
            )
            if fqdn.count('.') > 1:
                if fqdn.endswith('.'):
                    return fqdn
                return fqdn + '.'
        return super().get_fqdn()

    @classmethod
    def get_net_info(cls) -> dict:
        """
        Return network information dictionary.
        """
        info: dict = {}
        info['Net FQDN'] = cls.get_fqdn()
        task = subtask_mod.Batch(cls._get_ipconfig().get_cmdline())
        task.run()
        info['Net IPvx Address'] = []
        for line in task.get_output('IP.* Address'):
            info['Net IPvx Address'].append(
                line.replace('(Preferred)', '').split()[-1])
        info['Net IPvx DNS'] = []
        for line in task.get_output():
            if 'DNS Servers' in line:
                info['Net IPvx DNS'].append(line.split()[-1])
            elif info['Net IPvx DNS']:
                if ' : ' in line:
                    break
                info['Net IPvx DNS'].append(line.split()[-1])
        return info

    def get_os_info(self) -> dict:
        """
        Return operating system information dictionary.
        """
        info = {}
        info['OS Type'] = 'windows'
        info['OS Kernel X'] = 'NT'
        values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
        )[1]
        info['OS Name'] = self._isitset(values, 'ProductName')
        info['OS Kernel'] = command_mod.Platform.get_kernel()
        info['OS Patch'] = self._isitset(values, 'CSDVersion')
        patch_number = self._isitset(values, 'CSDBuildNumber')
        if patch_number == 'Unknown':
            info['OS Patch X'] = ''
        else:
            info['OS Patch X'] = patch_number
        return info

    def get_cpu_info(self) -> dict:
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()
        if 'AMD64' in (
                os.environ.get('PROCESSOR_ARCHITEW6432'),
                os.environ.get('PROCESSOR_ARCHITECTURE'),
        ):
            info['CPU Addressability'] = '64bit'
        else:
            info['CPU Addressability'] = '32bit'
        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE,
            r'HARDWARE\DESCRIPTION\System\CentralProcessor'
        )
        info['CPU Cores'] = str(len(subkeys))
        info['CPU Threads'] = info['CPU Cores']
        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\BIOS')

        if self._systeminfo.is_found():
            task = subtask_mod.Batch(self._systeminfo.get_cmdline())
            task.run()
            if self._has_value(values, 'RHEV') or task.is_match_output('RHEV'):
                info['CPU Cores X'] = 'RHEV VM'
            elif (
                    self._has_value(values, 'VMware') or
                    task.is_match_output('VMware')
            ):
                info['CPU Cores X'] = 'VMware VM'
            elif (
                    self._has_value(values, 'VirtualBox') or
                    task.is_match_output('VirtualBox')
            ):
                info['CPU Cores X'] = 'VirtualBox VM'

        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE,
            r'HARDWARE\DESCRIPTION\System\CentralProcessor\0'
        )
        info['CPU Model'] = re.sub(
            ' +',
            ' ',
            self._isitset(values, 'ProcessorNameString').strip()
        )
        info['CPU Clock'] = str(self._isitset(values, '~MHz'))
        return info

    def get_sys_info(self) -> dict:
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()

        if self._systeminfo.is_found():
            task = subtask_mod.Batch(self._systeminfo.get_cmdline())
            task.run()
            memory = task.get_output(':.*MB$')
            if memory:
                info['System Memory'] = memory[0].split()[-2].replace(',', '')
            if len(memory) > 2:
                info['System Swap Space'] = (
                    memory[4].split()[-2].replace(',', ''))
            try:
                info['System Uptime'] = re.sub(
                    '^[^:]*: *',
                    '',
                    task.get_output('^System Boot Time:')[0]
                )
            except IndexError:
                pass

        info['System Load'] = 'Unknown'
        return info

    @staticmethod
    def _reg_read(hive: Any, path: str) -> Tuple:
        subkeys = []
        values = {}
        try:
            key = winreg.OpenKey(hive, path)
            # pylint: disable = undefined-variable
        except WindowsError:  # type: ignore
            # pylint: enable = undefined-variable
            pass
        else:
            nsubkeys, nvalues = winreg.QueryInfoKey(key)[:2]
            for i in range(nsubkeys):
                subkeys.append(winreg.EnumKey(key, i))
            for i in range(nvalues):
                name, value, type_ = winreg.EnumValue(key, i)
                values[name] = [value, type_]
        return subkeys, values


class Writer:
    """
    Writer class
    """

    @staticmethod
    def dump(name: str, **kwargs: Any) -> None:
        """
        Dump information.
        """
        info = {name: kwargs}
        print(json.dumps(info, ensure_ascii=False, indent=4, sort_keys=True))

    @staticmethod
    def output(name: str, **kwargs: Any) -> None:
        """
        Output information.
        """
        line = f" {name + ':':19s}"
        if 'device' in kwargs and kwargs['device']:
            device = kwargs['device']
            if (
                    not device.startswith(('/dev/', 'net')) and
                    not os.path.exists(device)
            ):
                return
            line += f" {device:12s} {kwargs['value']}"
        elif 'location' in kwargs and kwargs['location']:
            line += f" {kwargs['location']}"
            if 'value' in kwargs and kwargs['value']:
                line += f"  {kwargs['value']}"
        elif 'value' in kwargs and kwargs['value']:
            line += f" {kwargs['value']}"
        if 'comment' in kwargs and kwargs['comment']:
            line += f" ({kwargs['comment']})"
        print(line)


class Software:
    """
    Software class
    """

    SOFTWARE_TOOLS = [
        (['bash', '--version'], ' version ', '.*version |[( ].*', ''),
        (['clamscan', '--version'], 'ClamAV ', '.*ClamAV |/.*', 'ClamAV'),
        (['convert', '--version'],
            ' ImageMagick ', '.*ImageMagick | .*', 'ImageMagick',),
        (['curl', '--version'], '^curl ', 'curl | .*', ''),
        (['dockerd', '--version'], ' version ', '.*version |,.*', 'Docker'),
        (['ffmpeg', '-version'],
            '^ffmpeg version ', '.*version | .*', 'FFmpeg'),
        (['gcc', '--version'], '^gcc ', '.* ', 'GCC'),
        (['g++', '--version'], '^g\\+\\+ ', '.* ', 'GCC'),
        (['gfortran', '--version'], '^GNU Fortran ', '.* ', 'GCC'),
        (['git', '--version'], 'version ', '.*version ', ''),
        (['git-lfs', '--version'], 'git-lfs/', 'git-lfs/| .*', ''),
        (['go', 'version'], r'version go\d', '.*version go| .*', 'Golang'),
        (['gpg', '--version'], r'GnuPG\) ', r'.*\)', 'GnuPG'),
        (['java', '--version'], '^openjdk ', 'openjdk | .*', 'OpenJDK'),
        (['javac', '--version'], '^javac ', 'javac | .*', ''),
        (['kubectl', 'version'], 'Client', '.*GitVersion:"v|".*', ''),
        (['helm', 'version'], 'Client', '.*SemVer:"v|".*', ''),
        (['htop', '-v'], '^htop ', 'htop | .*', ''),
        (['make', '--version'], 'GNU Make', '.*Make ', 'GNU Make'),
        (['python', '--version'], 'Python ', '.*Python ', ''),
        (['python3', '--version'], 'Python ', '.*Python ', ''),
        (['rsync', '--version'], '^rsync +version', 'rsync +version | .*', ''),
        (['sqlplus', '-V'], '^Version ', 'Version ', 'Instant Client'),
        (['ssh', '-V'], 'OpenSSH', '.*SSH[ _]| .*', 'OpenSSH'),
        (['systemctl', '--version'], '^systemd', 'systemd | .*', 'systemd'),
        (['tmux', '-V'], '^tmux ', '.* ', ''),
        (['wget', '--version'], 'Wget ', '.*Wget | .*', ''),
    ]

    def __init__(self) -> None:
        os.environ['KUBECONFIG'] = ''

        self._wrapper = []
        command = command_mod.Command('timeout', errors='ignore')
        if command.is_found():
            self._wrapper = command.get_cmdline() + ['-s', 'KILL', '1']

    def get(self, software: tuple) -> Tuple[str, str, str]:
        """
        Detect software
        """
        args, required, junk, comment = software

        command = command_mod.Command(args[0], args=args[1:], errors='ignore')
        if command.is_found():
            task = subtask_mod.Batch(self._wrapper + command.get_cmdline())
            task.run(pattern=required, error2output=True)
            if task.has_output():
                return (
                    command.get_file(),
                    re.sub(junk, '', task.get_output()[0]),
                    comment,
                )
        return None

    def detect(self) -> Generator[Tuple[str, str, str], None, None]:
        """
        Yield all software versions
        """
        for software in self.SOFTWARE_TOOLS:
            info = self.get(software)
            if info:
                yield info


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
            sys.exit(exception)
        sys.exit(0)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        detect = Detect(options)
        detect.show_banner()
        try:
            Detect(options).show_info()
        except subtask_mod.ExecutableCallError as exception:
            raise SystemExit(exception) from exception
        print()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
