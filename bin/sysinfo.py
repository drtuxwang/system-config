#!/usr/bin/env python3
"""
System configuration detection tool.

1996-2018 By Dr Colin Kong
"""

import functools
import glob
import json
import math
import os
import re
import signal
import socket
import sys
import threading
import time

import command_mod
import file_mod
import power_mod
import subtask_mod

if os.name == 'nt':
    # pylint: disable = import-error
    import winreg
    # pylint: enable = import-error

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")

RELEASE = '4.17.0'
VERSION = 20180516

# pylint: disable = too-many-lines


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release_date = str(
            VERSION)[:4] + '-' + str(VERSION)[4:6] + '-' + str(VERSION)[6:]
        self._release_version = RELEASE

        self._system = OperatingSystem.factory()

    def get_release_date(self):
        """
        Return release date.
        """
        return self._release_date

    def get_release_version(self):
        """
        Return release version.
        """
        return self._release_version

    def get_system(self):
        """
        Return operating system.
        """
        return self._system


class CommandThread(threading.Thread):
    """
    Command thread class
    """

    def __init__(self, command):
        threading.Thread.__init__(self, daemon=True)
        self._child = None
        self._command = command
        self._stdout = ''

    def run(self):
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

    def kill(self):
        """
        Kill thread
        """
        if self._child:
            self._child.kill()
            self._child = None

    def get_output(self):
        """
        Return thread output.
        """
        return self._stdout


class Detect(object):
    """
    Detect class
    """

    def __init__(self, options):
        self._author = ('Sysinfo ' + options.get_release_version() +
                        ' (' + options.get_release_date() + ')')

        self._system = options.get_system()

    def _network_information(self):
        info = self._system.get_net_info()
        Writer.output(
            name='Hostname',
            value=socket.gethostname().split('.')[0].lower()
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

    def _operating_system(self):
        info = self._system.get_os_info()
        Writer.output(name='OS Type', value=info['OS Type'])
        Writer.output(name='OS Name', value=info['OS Name'])
        Writer.output(
            name='OS Kernel',
            value=info['OS Kernel'],
            comment=info['OS Kernel X']
        )
        Writer.output(
            name='OS Patch',
            value=info['OS Patch'],
            comment=info['OS Patch X']
        )

    def _processors(self):
        info = self._system.get_cpu_info()
        Writer.output(name='CPU Type', value=info['CPU Type'])
        Writer.output(
            name='CPU Addressability',
            value=info['CPU Addressability'],
            comment=info['CPU Addressability X']
        )
        Writer.output(name='CPU Model', value=info['CPU Model'])
        Writer.output(name='CPU Sockets', value=info['CPU Sockets'])
        Writer.output(
            name='CPU Cores',
            value=info['CPU Cores'],
            comment=info['CPU Cores X']
        )
        Writer.output(
            name='CPU Threads',
            value=info['CPU Threads'],
            comment=info['CPU Threads X']
        )
        Writer.output(name='CPU Clock', value=info['CPU Clock'], comment='MHz')
        Writer.output(
            name='CPU Clocks',
            value=info['CPU Clocks'],
            comment='MHz'
        )
        for key, value in sorted(info['CPU Cache'].items()):
            Writer.output(
                name='CPU L' + key + ' Cache', value=value, comment='KB')

    def _system_status(self):
        info = self._system.get_sys_info()
        Writer.output(name='System Platform', value=info['System Platform'],
                      comment=info['System Platform X'])
        Writer.output(
            name='System Memory',
            value=info['System Memory'],
            comment='MB'
        )
        Writer.output(
            name='System Swap Space',
            value=info['System Swap Space'],
            comment='MB'
        )
        Writer.output(name='System Uptime', value=info['System Uptime'])
        Writer.output(name='System Load', value=info['System Load'],
                      comment='average over last 1min, 5min & 15min')

    @staticmethod
    def _xset():
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
                            value=standby + ' ' + suspend + ' ' + off,
                            comment='DPMS Standby Suspend Off'
                        )
                        break
                for line in task.get_output():
                    if 'auto repeat delay:' in line and 'repeat rate:' in line:
                        Writer.output(
                            name='X-Keyboard Repeat', value=line.split()[3],
                            comment=line.split()[6] + ' characters per second')
                        break
                for line in task.get_output():
                    if 'acceleration:' in line and 'threshold:' in line:
                        Writer.output(
                            name='X-Mouse Speed', value=line.split()[1],
                            comment='acceleration factor')
                        break
                for line in task.get_output():
                    if 'timeout:' in line and 'cycle:' in line:
                        timeout = int(line.split()[1])
                        if timeout:
                            Writer.output(
                                name='X-Screensaver',
                                value=str(timeout),
                                comment='no power saving for LCD but can '
                                'keep CPU busy'
                            )
                        break
            except (IndexError, ValueError):
                pass

    @staticmethod
    def _xrandr():
        xrandr = command_mod.Command('xrandr', errors='ignore')
        if xrandr.is_found():
            task = subtask_mod.Batch(xrandr.get_cmdline())
            task.run(pattern=' connected ')
            for line in task.get_output():
                try:
                    if ' connected ' in line:
                        columns = line.replace(
                            'primary ', '').replace('mm', '').split()
                        screen, _, resolution, *_, width, _, height = columns
                        if (width, height) == ('0', '0'):
                            Writer.output(
                                name="X-Windows Screen",
                                value=screen,
                                comment=resolution
                            )
                        else:
                            size = math.sqrt(
                                float(width)**2 + float(height)**2) / 25.4
                            comment = (
                                '{0:s}, {1:s}mm x {2:s}mm, {3:3.1f}"'.format(
                                    resolution, width, height, size)
                            )
                            Writer.output(
                                name='X-Windows Screen',
                                value=screen,
                                comment=comment
                            )
                except (IndexError, ValueError):
                    pass

    @staticmethod
    def _xwindows_screen(lines):
        if 'DISPLAY' in os.environ:
            width = '???'
            height = '???'
            try:
                for line in lines:
                    if 'Width:' in line:
                        width = line.split()[1]
                    elif 'Height:' in line:
                        height = line.split()[1]
                    elif 'Depth:' in line:
                        Writer.output(
                            name='X-Windows Server',
                            value=os.environ['DISPLAY'],
                            comment=width + 'x' + height + ', ' +
                            line.split()[1] + 'bit colour'
                        )
            except IndexError:
                pass

    @classmethod
    def _xwindows(cls):
        xwininfo = command_mod.Command(
            'xwininfo',
            pathextra=['/usr/bin/X11', '/usr/openwin/bin'],
            args=['-root'],
            errors='ignore'
        )
        if xwininfo.is_found():
            task = subtask_mod.Batch(xwininfo.get_cmdline())
            task.run()
            if task.has_output():
                cls._xset()
                cls._xrandr()
                cls._xwindows_screen(task.get_output())

    def show_banner(self):
        """
        Show banner.
        """
        timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')
        print("\n" + self._author, "- System configuration detection tool")
        print("\n*** Detected at", timestamp, "***")

    def show_info(self):
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


class OperatingSystem(object):
    """
    Operating system class
    """

    @staticmethod
    def detect_loader():
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
                except IndexError:
                    pass
                else:
                    Writer.output(
                        name='GNU C library',
                        location=glibc,
                        value=version
                    )
        for linker in sorted(glob.glob('/lib*/ld-*so*')):
            Writer.output(name='Dynamic linker', location=linker)

    @staticmethod
    def has_devices():
        """
        Return False
        """
        return False

    @staticmethod
    def has_loader():
        """
        Return False
        """
        return False

    @staticmethod
    def get_fqdn():
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        fqdn = (socket.getfqdn()).lower()
        if fqdn.count('.') < 2:
            return 'Unknown'
        if fqdn.endswith('.'):
            return fqdn
        return fqdn + '.'

    @classmethod
    def get_net_info(cls):
        """
        Return network information dictionary.
        """
        info = {}
        info['Net FQDN'] = cls.get_fqdn()
        info['Net IPvx Address'] = []
        info['Net IPvx DNS'] = []
        return info

    @staticmethod
    def get_os_info():
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
        return info

    @staticmethod
    def get_cpu_info():
        """
        Return CPU information dictionary.
        """
        info = {}
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

    @staticmethod
    def get_sys_info():
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
    def _has_value(values, word):
        for value in values.values():
            if word in str(value[0]):
                return True
        return False

    @staticmethod
    def _isitset(values, name):
        if name in values:
            return values[name][0]
        return 'Unknown'

    @staticmethod
    def factory():
        """
        Return OperatignSystem sub class
        """

        if os.name == 'nt':
            return WindowsSystem()

        osname = os.uname()[0]
        if osname == 'Darwin':
            return MacSystem()
        elif osname == 'Linux':
            return LinuxSystem()

        return OperatingSystem()


class PosixSystem(OperatingSystem):
    """
    Posix system class
    """

    @staticmethod
    def _detect_battery():
        batteries = power_mod.Battery.factory()

        for battery in batteries:
            if battery.is_exist():
                model = (
                    battery.get_oem() + ' ' + battery.get_name() +
                    ' ' + battery.get_type() + ' ' +
                    str(battery.get_capacity_max()) + 'mAh/' +
                    str(battery.get_voltage()) + 'mV'
                )
                if battery.get_charge() == '-':
                    state = '-'
                    if battery.get_rate() > 0:
                        state += str(battery.get_rate()) + 'mA'
                        if battery.get_voltage() > 0:
                            mywatts = '{0:4.2f}'.format(float(
                                battery.get_rate() * battery.get_voltage()
                            ) / 1000000)
                            state += ', ' + str(mywatts) + 'W'
                        hours = '{0:3.1f}'.format(
                            float(battery.get_capacity()) / battery.get_rate())
                        state += ', ' + str(hours) + 'h'
                elif battery.get_charge() == '+':
                    state = '+'
                    if battery.get_rate() > 0:
                        state += str(battery.get_rate()) + 'mA'
                        if battery.get_voltage() > 0:
                            mywatts = '{0:4.2f}'.format(float(
                                battery.get_rate() * battery.get_voltage()
                            ) / 1000000)
                            state += ', ' + str(mywatts) + 'W'
                else:
                    state = 'Unused'
                Writer.output(name='Battery device', device='/dev/???',
                              value=str(battery.get_capacity()) + 'mAh',
                              comment=model + ' [' + state + ']')

    @classmethod
    def detect_devices(cls):
        """
        Detect devices
        """
        cls._detect_battery()

    @staticmethod
    def has_devices():
        return True

    @classmethod
    def get_fqdn(cls):
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        ispattern = re.compile(r'\s*(domain|search)\s')
        try:
            with open('/etc/resolv.conf', errors='replace') as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        fqdn = socket.gethostname(
                            ).split('.')[0].lower() + '.' + line.split()[1]
                        if fqdn.endswith('.'):
                            return fqdn
                        return fqdn + '.'
        except (IndexError, OSError):
            pass
        return super().get_fqdn()

    def get_net_info(self):
        """
        Return network information dictionary.
        """
        info = super().get_net_info()
        ispattern = re.compile(r'\s*nameserver\s*\d')
        try:
            with open('/etc/resolv.conf', errors='replace') as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        info['Net IPvx DNS'].append(line.split()[1])
        except (IndexError, OSError):
            pass
        return info

    def get_os_info(self):
        """
        Return operating system information dictionary.
        """
        info = super().get_os_info()
        info['OS Kernel'] = command_mod.Platform.get_kernel()
        info['OS Kernel X'] = os.uname()[0]
        return info

    def get_cpu_info(self):
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()
        return info

    def get_sys_info(self):
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

    def __init__(self):
        device = None
        self._devices = {}
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
                                driver + ' driver ' +
                                task2.get_output()[0].split()[1]
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
    def _scan_vga(line, device, modinfo):
        device = ''
        if 'nvidia' in line.lower():
            try:
                with open(
                    '/proc/driver/nvidia/version',
                    errors='replace'
                ) as ifile:
                    for line2 in ifile:
                        if 'Kernel Module ' in line2:
                            device = 'nvidia driver ' + line2.split(
                                'Kernel Module ')[1].split()[0]
            except OSError:
                pass
        elif 'VirtualBox' in line and modinfo.is_found():
            task2 = subtask_mod.Batch(modinfo.get_cmdline() + ['vboxvideo'])
            task2.run(pattern='^(version|vermagic):')
            if task2.has_output():
                device = (
                    'vboxvideo driver ' + task2.get_output()[0].split()[1])

        return device

    @staticmethod
    def _detect_audio_device(device, name):
        if device.endswith('p'):
            Writer.output(
                name='Audio device',
                device=device,
                value=name,
                comment='SPK'
            )
        else:
            Writer.output(
                name='Audio device',
                device=device,
                value=name,
                comment='MIC'
            )

    @staticmethod
    def _detect_audio_proc(card, model):
        if card == '0':
            unit = ''
        else:
            unit = card
        if glob.glob('/proc/asound/card' + card + '/midi*'):
            device = '/dev/midi' + unit
            if not os.path.exists(device):
                device = '/dev/???'
            Writer.output(
                name='Audio device',
                device=device,
                value=model,
                comment='MIDI'
            )
        device = '/dev/dsp' + unit
        if not os.path.exists(device):
            device = '/dev/???'
        if glob.glob('/proc/asound/card' + card + '/pcm*c'):
            if glob.glob('/proc/asound/card' + card + '/pcm*p'):
                Writer.output(
                    name='Audio device',
                    device=device,
                    value=model,
                    comment='MIC/SPK'
                )
            else:
                Writer.output(
                    name='Audio device',
                    device=device,
                    value=model,
                    comment='MIC'
                )
        elif glob.glob('/proc/asound/card' + card + '/pcm*p'):
            Writer.output(
                name='Audio device',
                device=device,
                value=model,
                comment='SPK'
            )

    @classmethod
    def _detect_audio(cls):
        lines = []
        ispattern = re.compile(r' ?\d+ ')
        try:
            with open('/proc/asound/cards', errors='replace') as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        lines.append(line.rstrip('\r\n'))
        except OSError:
            pass
        if lines:
            for line in lines:
                try:
                    card = line.split()[0]
                    model = line.split(': ')[1].split('- ')[-1]
                except IndexError:
                    continue
                for file in sorted(glob.glob(
                        '/proc/asound/card' + card + '/pcm*[cp]/info')):
                    try:
                        with open(file, errors='replace') as ifile:
                            for line2 in ifile:
                                if line2.startswith('name: '):
                                    name = model + ' ' + line2.rstrip(
                                        '\r\n').replace('name: ', '', 1)
                    except (IndexError, OSError):
                        continue

                    device = (
                        '/dev/snd/pcmC' + card + 'D' +
                        os.path.dirname(file).split('pcm')[-1]
                    )

                    if os.path.exists(device):
                        cls._detect_audio_device(device, name)
                    else:
                        cls._detect_audio_proc(card, model)

    @staticmethod
    def _detect_cd_proc_ide():
        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                with open(
                    os.path.join(directory, 'driver'),
                    errors='replace'
                ) as ifile:
                    for line in ifile:
                        if line.startswith('ide-cdrom '):
                            with open(
                                os.path.join(directory, 'model'),
                                errors='replace'
                            ) as ifile:
                                model = ifile.readline().strip()
                                Writer.output(
                                    name='CD device',
                                    device='/dev/' +
                                    os.path.basename(directory),
                                    value=model
                                )
                                break
            except OSError:
                pass

    @staticmethod
    def _detect_cd_sys_scsi():
        for file in sorted(glob.glob('/sys/block/sr*/device')):  # New kernels
            try:
                identity = os.path.basename(os.readlink(file))
            except OSError:
                continue
            try:
                if os.path.isdir('/sys/bus/scsi/devices/' + identity):
                    with open(
                        os.path.join(
                            '/sys/bus/scsi/devices', identity, 'vendor'),
                        errors='replace'
                    ) as ifile:
                        model = ifile.readline().strip()
                    with open(
                        os.path.join(
                            '/sys/bus/scsi/devices', identity, 'model'),
                        errors='replace'
                    ) as ifile:
                        model += ' ' + ifile.readline().strip()
            except OSError:
                model = '???'
            device = '/dev/' + os.path.basename(os.path.dirname(file))
            Writer.output(name='CD device', device=device, value=model)

    @staticmethod
    def _detect_cd_proc_scsi():
        model = '???'
        unit = 0
        isjunk = re.compile('.*Vendor: | *Model:| *Rev: .*')
        try:
            with open('/proc/scsi/scsi', errors='replace') as ifile:
                for line in ifile:
                    if 'Vendor: ' in line and 'Model: ' in line:
                        model = isjunk.sub('', line.rstrip('\r\n'))
                    elif 'Type:' in line and 'CD-ROM' in line:
                        if os.path.exists('/dev/sr' + str(unit)):
                            device = '/dev/sr' + str(unit)
                        else:
                            device = '/dev/scd' + str(unit)
                        Writer.output(
                            name='CD device',
                            device=device,
                            value=model
                        )
                        model = '???'
                        unit += 1
        except OSError:
            pass

    @classmethod
    def _detect_cd(cls):
        cls._detect_cd_proc_ide()

        if os.path.isdir('/sys/bus/scsi/devices'):
            cls._detect_cd_sys_scsi()
        else:
            cls._detect_cd_proc_scsi()

    @staticmethod
    def _get_disk_info():
        info = {}
        info['partitions'] = []
        info['swaps'] = []
        try:
            with open('/proc/partitions', errors='replace') as ifile:
                for line in ifile:
                    info['partitions'].append(line.rstrip('\r\n'))
        except OSError:
            pass
        try:
            with open('/proc/swaps', errors='replace') as ifile:
                for line in ifile:
                    if line.startswith('/dev/'):
                        info['swaps'].append(line.split()[0])
        except OSError:
            pass
        return info

    @staticmethod
    def _scan_mounts(info):
        info['mounts'] = {}
        try:
            with open('/proc/mounts', errors='replace') as ifile:
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
            with open('/proc/swaps', errors='replace') as ifile:
                for line in ifile:
                    if line.startswith('/dev/'):
                        info['swaps'].append(line.split()[0])
        except OSError:
            pass

    @staticmethod
    def _detect_ide_partition(info, model, hdx, partition):
        if partition.endswith(hdx) or hdx + ' ' in partition:
            try:
                size = partition.split()[2]
            except IndexError:
                size = '???'
            Writer.output(
                name='Disk device',
                device='/dev/' + hdx,
                value=size + ' KB',
                comment=model
            )
        elif hdx in partition:
            size, hdxn = partition.split()[2:4]
            device = '/dev/' + hdxn
            comment = ''
            if device in info['swaps']:
                comment = 'swap'
            elif device in info['mounts']:
                for mount_point, mount_type in info[
                        'mounts'][device]:
                    comment = mount_type + ' on ' + mount_point
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=size + ' KB',
                        comment=comment
                    )
                return
            else:
                comment = ''
            Writer.output(
                name='Disk device',
                device=device,
                value=size + ' KB',
                comment=comment
            )

    @classmethod
    def _detect_disk_ide(cls, info, directory):
        with open(
            os.path.join(directory, 'driver'),
            errors='replace'
        ) as ifile:
            for line in ifile:
                if line.startswith('ide-disk '):
                    file = os.path.join(directory, 'model')
                    with open(file, errors='replace') as ifile2:
                        model = ifile2.readline().rstrip('\r\n')
                    hdx = os.path.basename(directory)
                    for partition in info['partitions']:
                        cls._detect_ide_partition(info, model, hdx, partition)

    @staticmethod
    def _get_disk_sys_scsi_model(file):
        try:
            identity = os.path.basename(os.readlink(file))
        except OSError:
            return None

        try:
            if os.path.isdir('/sys/bus/scsi/devices/' + identity):
                with open(
                    os.path.join('/sys/bus/scsi/devices', identity, 'vendor'),
                    errors='replace'
                ) as ifile:
                    model = ifile.readline().strip()
                with open(os.path.join(
                    '/sys/bus/scsi/devices', identity, 'model'
                ), errors='replace') as ifile:
                    model += ' ' + ifile.readline().strip()
        except OSError:
            model = '???'

        return model

    @classmethod
    def _detect_disk_sys_scsi(cls, info, file):
        model = cls._get_disk_sys_scsi_model(file)

        sdx = os.path.basename(os.path.dirname(file))
        for partition in info['partitions']:
            if partition.endswith(sdx) or sdx + ' ' in partition:
                try:
                    size = partition.split()[2]
                except IndexError:
                    size = '???'
                device = '/dev/' + sdx
                if device in info['mounts']:
                    for mount_point, mount_type in info['mounts'][device]:
                        comment = mount_type + ' on ' + mount_point
                        Writer.output(
                            name='Disk device',
                            device=device,
                            value=size + ' KB',
                            comment=comment + ', ' + model
                        )
                    continue
                else:
                    Writer.output(
                        name='Disk device',
                        device='/dev/' + sdx,
                        value=size + ' KB',
                        comment=model
                    )
            elif sdx in partition:
                size, sdxn = partition.split()[2:4]
                device = '/dev/' + sdxn
                if device in info['swaps']:
                    comment = 'swap'
                elif device in info['mounts']:
                    for mount_point, mount_type in info['mounts'][device]:
                        comment = mount_type + ' on ' + mount_point
                        Writer.output(
                            name='Disk device',
                            device=device,
                            value=size + ' KB',
                            comment=comment
                        )
                    continue
                elif glob.glob('/sys/class/block/dm-*/slaves/' + sdxn):
                    comment = 'devicemapper'
                else:
                    comment = ''
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=size + ' KB',
                    comment=comment
                )

    @staticmethod
    def _detect_disk_proc_scsi_part(info, unit, model):
        sdx = 'sd' + chr(97 + unit)
        if os.path.exists('/dev/' + sdx):
            for partition in info['partitions']:
                if partition.endswith(sdx) or sdx + ' ' in partition:
                    try:
                        size = partition.split()[2]
                    except IndexError:
                        size = '???'
                    Writer.output(
                        name='Disk device',
                        device='/dev/' + sdx,
                        value=size + ' KB',
                        comment=model
                    )
                elif sdx in partition:
                    size, sdxn = partition.split()[2:4]
                    device = '/dev/' + sdxn
                    if device in info['swaps']:
                        comment = 'swap'
                    elif device in info['mounts']:
                        for mount_point, mount_type in info['mounts'][device]:
                            comment = mount_type + ' on ' + mount_point
                            Writer.output(
                                name='Disk device',
                                device=device,
                                value=size + ' KB',
                                comment=comment
                            )
                        continue
                    else:
                        comment = ''
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=size + ' KB',
                        comment=comment
                    )

    @classmethod
    def _detect_disk_proc_scsi(cls, info):
        model = '???'
        unit = 0
        isjunk = re.compile('.*Vendor: | *Model:| *Rev: .*')
        try:
            with open('/proc/scsi/scsi', errors='replace') as ifile:
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
    def _detect_mapped_disks(info):
        for directory in glob.glob('/sys/class/block/dm-*'):
            file = os.path.join(directory, 'dm/name')
            try:
                with open(file, errors='replace') as ifile:
                    device = '/dev/mapper/' + ifile.readline().strip()
            except OSError:
                device = '???'
            mount_info = info['mounts'].get(device, ())

            slaves = '+'.join([os.path.basename(file) for file in glob.glob(
                os.path.join(directory, 'slaves', '*')
            )])

            file = os.path.join(directory, 'size')
            try:
                with open(file, errors='replace') as ifile:
                    size = '{0:d} KB'.format(int(ifile.readline()) >> 1)
            except (OSError, ValueError):
                size = '??? KB'

            file = os.path.join(directory, 'dm', 'uuid')
            try:
                with open(file, errors='replace') as ifile:
                    slaves = ifile.readline().split('-')[0] + ':' + slaves
            except (OSError, ValueError):
                slaves = '???:' + slaves

            if '/dev/' + os.path.basename(directory) in info['swaps']:
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=size,
                    comment='swap, ' + slaves
                )
            else:
                for mount_point, mount_type in mount_info:
                    Writer.output(
                        name='Disk device',
                        device=device,
                        value=size,
                        comment='{0:s} on {1:s}, {2:s}'.format(
                            mount_type,
                            mount_point,
                            slaves
                        )
                    )

    @staticmethod
    def _detect_remote_disks(info):
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
                    comment=mount_type + ' on ' + mount_point
                )

    @classmethod
    def _detect_disk(cls):
        info = cls._get_disk_info()
        cls._scan_mounts(info)

        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                cls._detect_disk_ide(info, directory)
            except OSError:
                pass

        if os.path.isdir('/sys/bus/scsi/devices'):  # New kernels
            for file in sorted(glob.glob('/sys/block/*d[a-z]*/device')):
                cls._detect_disk_sys_scsi(info, file)
        else:
            cls._detect_disk_proc_scsi(info)
        cls._detect_mapped_disks(info)
        cls._detect_remote_disks(info)

    def _detect_ethernet(self):
        # Ethernet device detection
        for line, device in sorted(self._devices.items()):
            if 'Ethernet controller: ' in line:
                model = line.split('Ethernet controller: ')[1].replace(
                    'Semiconductor ', '').replace('Co., ', '').replace(
                        'Ltd. ', '').replace('PCI Express ', '')
                Writer.output(
                    name='Ethernet device',
                    device='/dev/???',
                    value=model,
                    comment=device
                )

    def _detect_firewire(self):
        for line, device in sorted(self._devices.items()):
            if 'FireWire (IEEE 1394): ' in line:
                model = line.split('FireWire (IEEE 1394): ')[1]
                Writer.output(
                    name='Firewire device',
                    device='/dev/???',
                    value=model,
                    comment=device)

    def _detect_graphics(self):
        for line, device in sorted(self._devices.items()):
            if 'VGA compatible controller: ' in line:
                model = line.split('VGA compatible controller: ')[1].strip()
                Writer.output(
                    name='Graphics device',
                    device='/dev/???',
                    value=model,
                    comment=device
                )

    def _detect_inifiniband(self):
        for line, device in sorted(self._devices.items()):
            if 'InfiniBand: ' in line:
                model = line.split(
                    'InfiniBand: ')[1].replace('InfiniHost', 'InifiniBand')
                Writer.output(
                    name='InifiniBand device',
                    device='/dev/???',
                    value=model,
                    comment=device
                )

    @staticmethod
    def _detect_input():
        info = {}
        for file in glob.glob('/dev/input/by-path/*event*'):
            try:
                device = '/dev/input/' + os.path.basename(os.readlink(file))
                if os.path.exists(device):
                    info[device] = os.path.basename(
                        file).replace('-event', '').replace('-', ' ')
            except OSError:
                continue

        isjunk = re.compile(r'/usb-\w{4}_\w{4}-')
        for file in glob.glob('/dev/input/by-id/*event*'):
            try:
                device = '/dev/input/' + os.path.basename(os.readlink(file))
                if os.path.exists(device) and not isjunk.search(file):
                    info[device] = os.path.basename(
                        file).split('-')[1].replace('_', ' ')
            except (IndexError, OSError):
                continue
        for key, value in sorted(info.items()):
            Writer.output(name='Input device', device=key, value=value)

    def _detect_network(self):
        for line, device in sorted(self._devices.items()):
            if 'Network controller: ' in line:
                model = line.split(': ', 1)[1].split(' (')[0]
                Writer.output(
                    name='Network device',
                    device='/dev/???',
                    value=model,
                    comment=device
                )

    @staticmethod
    def _detect_video():
        for directory in sorted(glob.glob('/sys/class/video4linux/*')):
            device = os.path.basename(directory)
            try:
                with open(
                    os.path.join(directory, 'name'),
                    errors='replace'
                ) as ifile:
                    Writer.output(
                        name='Video device',
                        device='/dev/' + device,
                        value=ifile.readline().rstrip('\r\n')
                    )
                    continue
            except OSError:
                pass
            Writer.output(
                name='Video device',
                device='/dev/' + device, value='???'
            )

    def detect_devices(self):
        """
        Detect devices
        """
        self._detect_audio()
        self._detect_battery()
        self._detect_cd()
        self._detect_disk()
        self._detect_ethernet()
        self._detect_firewire()
        self._detect_graphics()
        self._detect_inifiniband()
        self._detect_input()
        self._detect_network()
        self._detect_video()

    def has_loader(self):
        """
        Return True
        """
        return True

    def get_net_info(self):
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
    def _scan_etc_release():
        info = {}

        if os.path.isfile('/etc/redhat-release'):
            try:
                with open('/etc/redhat-release', errors='replace') as ifile:
                    info['OS Name'] = ifile.readline().rstrip('\r\n')
            except OSError:
                pass
        elif os.path.isfile('/etc/SuSE-release'):
            try:
                with open('/etc/SuSE-release', errors='replace') as ifile:
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
                with open('/etc/alpine-release', errors='replace') as ifile:
                    info['OS Name'] = (
                        'Alpine ' + ifile.readline().rstrip('\r\n')
                    )
            except OSError:
                pass

        return info

    @staticmethod
    def _scan_etc_lsb_release():
        info = {}

        if os.path.isfile('/etc/lsb-release'):
            try:
                with open('/etc/lsb-release', errors='replace') as ifile:
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
                            info['OS Name'] = identity + ' ' + line.split(
                                '=')[1]
                            break

        return info

    @staticmethod
    def _scan_etc_version():
        info = {}

        if os.path.isfile('/etc/kanotix-version'):
            try:
                with open(
                    '/etc/kanotix-version',
                    errors='replace'
                ) as ifile:
                    info['OS Name'] = 'Kanotix ' + ifile.readline(
                        ).rstrip('\r\n').split()[1]
            except (IndexError, OSError):
                pass
        elif os.path.isfile('/etc/knoppix-version'):
            try:
                with open('/etc/knoppix-version', errors='replace') as ifile:
                    info['OS Name'] = 'Knoppix ' + ifile.readline(
                        ).rstrip('\r\n').split()[0]
            except (IndexError, OSError):
                pass
        elif os.path.isfile('/etc/debian_version'):
            try:
                with open('/etc/debian_version', errors='replace') as ifile:
                    info['OS Name'] = 'Debian ' + ifile.readline().rstrip(
                        '\r\n').split('=')[-1].replace("'", '')
            except OSError:
                pass
        elif os.path.isfile('/etc/DISTRO_SPECS'):
            try:
                identity = None
                with open('/etc/DISTRO_SPECS', errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('DISTRO_NAME'):
                            identity = line.rstrip(
                                '\r\n').split('=')[1].replace('"', '')
                        elif line.startswith('DISTRO_VERSION') and identity:
                            info['OS Name'] = identity + ' ' + line.rstrip(
                                '\r\n').split('=')[1]
                            break
            except (IndexError, OSError):
                pass

        return info

    @staticmethod
    def _scan_dpkg_version():
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
                            'Knoppix ' + line.split()[2].split('-')[0])
                        return info
                    elif package == 'mepis-auto':
                        info['OS Name'] = 'MEPIS ' + line.split()[2]
                        return info
                    elif ' kernel ' in line and 'MEPIS' in line:
                        isjunk = re.compile('MEPIS.')
                        info['OS Name'] = 'MEPIS ' + isjunk.sub(
                            '', line.split()[2])
                        return info
                except IndexError:
                    pass
            for line in task.get_output():
                try:
                    package = line.split()[1]
                    if package == 'base-files':
                        info['OS Name'] = 'Debian ' + line.split()[2]
                        return info
                except IndexError:
                    pass
            return info

        return info

    @staticmethod
    def _scan_os_release():
        info = {}

        try:
            with open('/etc/os-release', errors='replace') as ifile:
                for line in ifile:
                    if line.startswith('PRETTY_NAME="'):
                        info['OS Name'] = line.split('"')[1].split('(')[0]
                        break
        except OSError:
            pass

        return info

    @staticmethod
    def _scan_clear_version():
        info = {}

        try:
            with open('/usr/share/clear/version', errors='replace') as ifile:
                info['OS Name'] = 'Clear Linux ' + ifile.readline().strip()
        except OSError:
            pass

        return info

    def get_os_info(self):
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

        return info

    @staticmethod
    def _scan_frequency(info, lines):
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq',
                      errors='replace') as ifile:
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
                errors='replace'
            ) as ifile:
                for clock in ifile.readline().rstrip('\r\n').split():
                    found.append(str(int(int(clock) / 1000 + 0.5)))
                if found:
                    info['CPU Clocks'] = ' '.join(found)
        except (OSError, ValueError):
            try:
                with open(
                    '/sys/devices/system/cpu/cpu0/cpufreq/'
                    'scaling_max_freq',
                    errors='replace'
                ) as ifile:
                    info['CPU Clocks'] = str(int(
                        int(ifile.readline()) / 1000 + 0.5))
                with open(
                    '/sys/devices/system/cpu/cpu0/cpufreq/'
                    'scaling_min_freq',
                    errors='replace'
                ) as ifile:
                    info['CPU Clocks'] += ' ' + str(int(
                        int(ifile.readline()) / 1000 + 0.5))
            except (OSError, ValueError):
                info['CPU Clocks'] = 'Unknown'

    @staticmethod
    def _get_proc_cpuinfo():
        lines = []
        try:
            with open('/proc/cpuinfo', errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except OSError:
            pass

        return lines

    @staticmethod
    def _scan_cpu_model(info, lines):
        isspace = re.compile(r'\s+')

        try:
            if command_mod.Platform.get_arch() == 'Power':
                for line in lines:
                    if line.startswith('cpu'):
                        info['CPU Model'] = 'PowerPC_' + isspace.sub(
                            ' ', line.split(': ')[1].split(' ')[0].strip())
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
    def _get_cpu_threads(lines):
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
    def _get_cpu_physical_packages():
        found = []

        for file in glob.glob(
                '/sys/devices/system/cpu/cpu[0-9]*/'
                'topology/physical_package_id'
        ):
            try:
                with open(file, errors='replace') as ifile:
                    line = ifile.readline().rstrip('\r\n')
                    if line not in found:
                        found.append(line)
            except OSError:
                pass

        return found

    @classmethod
    def _get_cpu_sockets(cls, lines, threads):
        found = cls._get_cpu_physical_packages()
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
                            sockets = threads / int(line.split()[2])
                        except (IndexError, ValueError):
                            pass
                        break
        return sockets

    @staticmethod
    def _get_cpu_cores(info, lines, sockets, threads):
        try:
            with open(
                '/sys/devices/system/cpu/cpu0/topology/'
                'thread_siblings_list',
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
    def _scan_cache(info, lines):
        for cache in sorted(glob.glob(
                '/sys/devices/system/cpu/cpu0/cache/index*')):
            try:
                with open(
                    os.path.join(cache, 'level'),
                    errors='replace'
                ) as ifile:
                    level = ifile.readline().rstrip('\r\n')
                with open(
                    os.path.join(cache, 'type'),
                    errors='replace'
                ) as ifile:
                    type_ = ifile.readline().rstrip('\r\n')
                if type_ == 'Data':
                    level += 'd'
                elif type_ == 'Instruction':
                    level += 'i'
                with open(
                    os.path.join(cache, 'size'),
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

    def get_cpu_info(self):
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
                info['CPU Cores X'] = '{0:s} container, {1:s} VM'.format(
                    container,
                    virtual_machine
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

    def get_sys_info(self):
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()
        try:
            with open('/proc/meminfo', errors='replace') as ifile:
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
    def _get_container():
        name = None
        try:
            with open('/proc/1/cgroup', errors='replace') as ifile:
                for line in ifile:
                    if '/docker/' in line:
                        name = 'Docker'
                        break
                    elif '/lxc/' in line:
                        name = 'LXC'
                        break
        except OSError:
            pass
        return name

    @staticmethod
    def _check_virtual_machine(data, mapping):
        for vendor, text in mapping.items():
            if text in data:
                return vendor
        return None

    def _get_virtual_machine(self):
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
                    with open(file, errors='replace') as ifile:
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

    def __init__(self):
        sysctl = command_mod.CommandFile('/usr/sbin/sysctl', args=['-a'])
        task = subtask_mod.Batch(sysctl.get_cmdline())
        task.run()

        # ' = ' is used in older versions of MacOS
        self._kernel_settings = [
            x.replace(' = ', ': ', 1) for x in task.get_output()]

    @staticmethod
    def _detect_disk():
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
                task.run(pattern='^' + device + ' .* ')
                for line2 in task.get_output():
                    size = line2.split()[1]
                    break
                else:
                    size = '???'
                Writer.output(
                    name='Disk device',
                    device=device,
                    value=size + ' KB', comment=type_ + ' on ' + directory
                )

    @classmethod
    def detect_devices(cls):
        """
        Detect devices
        """
        cls._detect_battery()
        cls._detect_disk()

    def get_net_info(self):
        """
        Return network information dictionary.
        """
        info = super().get_net_info()
        ifconfig = command_mod.CommandFile('/sbin/ifconfig', args=['-a'])
        task = subtask_mod.Batch(ifconfig.get_cmdline())
        task.run(pattern='inet[6]? ')
        isjunk = re.compile('.*inet[6]? ')
        for line in task.get_output():
            info['Net IPvx Address'].append(isjunk.sub(' ', line).split()[0])
        return info

    def get_os_info(self):
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

    def _get_cpu_socket_info(self):
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

    def get_cpu_info(self):
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
                    '{0:d}'.format(int(int(line.split(': ', 1)[1]) / 1024)))

        return info

    def get_sys_info(self):
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

    def __init__(self):
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
    def _get_ipconfig():
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
    def get_fqdn(cls):
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        task = subtask_mod.Batch(cls._get_ipconfig().get_cmdline())
        task.run()
        for line in task.get_output('Connection-specific DNS Suffix'):
            fqdn = socket.gethostname(
                ).split('.')[0].lower() + '.' + line.split()[-1]
            if fqdn.count('.') > 1:
                if fqdn.endswith('.'):
                    return fqdn
                return fqdn + '.'
        return super().get_fqdn()

    @classmethod
    def get_net_info(cls):
        """
        Return network information dictionary.
        """
        info = {}
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

    def get_os_info(self):
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

    def get_cpu_info(self):
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

    def get_sys_info(self):
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
    def _reg_read(hive, path):
        subkeys = []
        values = {}
        try:
            key = winreg.OpenKey(hive, path)
        # pylint: disable = undefined-variable
        except WindowsError:
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


class Writer(object):
    """
    Writer class
    """

    @staticmethod
    def dump(name, **kwargs):
        """
        Dump information.
        """
        info = {name: kwargs}
        print(json.dumps(info, indent=4, sort_keys=True))

    @staticmethod
    def output(name, **kwargs):
        """
        Output information.
        """
        line = ' {0:19s}'.format(name + ':')
        if 'device' in kwargs and kwargs['device']:
            line += ' {0:12s}'.format(kwargs['device']) + ' ' + kwargs['value']
        elif 'location' in kwargs and kwargs['location']:
            line += ' ' + kwargs['location']
            if 'value' in kwargs and kwargs['value']:
                line += '  ' + kwargs['value']
        elif 'value' in kwargs and kwargs['value']:
            line += ' ' + kwargs['value']
        if 'comment' in kwargs and kwargs['comment']:
            line += ' (' + kwargs['comment'] + ')'
        print(line)


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
        sys.exit(0)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        detect = Detect(options)
        detect.show_banner()
        try:
            Detect(options).show_info()
        except subtask_mod.ExecutableCallError as exception:
            raise SystemExit(exception)
        print()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
