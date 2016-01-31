#!/usr/bin/env python3
"""
System configuration detection tool.

1996-2016 By Dr Colin Kong
"""

import glob
import math
import os
import re
import signal
import socket
import sys
import threading
import time

import ck_battery
import syslib

RELEASE = '4.6.4'
VERSION = 20160130

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable = import-error, wrong-import-position

if os.name == 'nt':
    import winreg

# pylint: disable = no-self-use, too-few-public-methods
# pylint: disable = too-many-lines, too-many-nested-blocks, undefined-variable
# pylint: disable = too-many-nested-blocks, too-many-return-statements, too-many-arguments
# pylint: disable = too-many-statements, too-many-locals, too-many-branches
# pylint: disable = too-many-instance-attributes, super-init-not-called


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release_date = str(VERSION)[:4] + '-' + str(VERSION)[4:6] + '-' + str(VERSION)[6:]
        self._release_version = RELEASE

        self._system = self._get_system()

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
        Return operating syslib.
        """
        return self._system

    def _get_system(self):
        name = syslib.info.get_system()
        if name == 'linux':
            return LinuxSystem()
        elif name == 'windows':
            return WindowsSystem()
        else:
            return OperatingSystem()


class CommandThread(threading.Thread):
    """
    Command thread class
    """

    def __init__(self, command):
        threading.Thread.__init__(self)
        self._child = None
        self._command = command
        self._stdout = ''

    def run(self):
        """
        Run thread
        """
        self._child = self._command.run(mode='child')
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
        self._writer = Writer(options)

    def _network_information(self):
        info = self._system.get_net_info()
        self._writer.output(name='Hostname', value=syslib.info.get_hostname())
        self._writer.output(name='Net FQDN', value=info['Net FQDN'])

        for address in info['Net IPvx Address']:
            if ':' in address:
                self._writer.output(name='Net IPv6 Address', value=address)
            else:
                self._writer.output(name='Net IPv4 Address', value=address)

        for address in info['Net IPvx DNS']:
            if ':' in address:
                self._writer.output(name='Net IPv6 DNS', value=address)
            else:
                self._writer.output(name='Net IPv4 DNS', value=address)

    def _operating_system(self):
        info = self._system.get_os_info()
        self._writer.output(name='OS Type', value=info['OS Type'])
        self._writer.output(name='OS Name', value=info['OS Name'])
        self._writer.output(name='OS Kernel', value=info['OS Kernel'],
                            comment=info['OS Kernel X'])
        self._writer.output(name='OS Patch', value=info['OS Patch'],
                            comment=info['OS Patch X'])

    def _processors(self):
        info = self._system.get_cpu_info()
        self._writer.output(name='CPU Type', value=info['CPU Type'])
        self._writer.output(name='CPU Addressability', value=info['CPU Addressability'],
                            comment=info['CPU Addressability X'])
        self._writer.output(name='CPU Model', value=info['CPU Model'])
        self._writer.output(name='CPU Sockets', value=info['CPU Sockets'])
        self._writer.output(name='CPU Cores', value=info['CPU Cores'], comment=info['CPU Cores X'])
        self._writer.output(name='CPU Threads', value=info['CPU Threads'],
                            comment=info['CPU Threads X'])
        self._writer.output(name='CPU Clock', value=info['CPU Clock'], comment='MHz')
        self._writer.output(name='CPU Clocks', value=info['CPU Clocks'], comment='MHz')
        for key, value in sorted(info['CPU Cache'].items()):
            self._writer.output(name='CPU L' + key + ' Cache', value=value, comment='KB')

    def _system_status(self):
        info = self._system.get_sys_info()
        self._writer.output(name='System Platform', value=info['System Platform'],
                            comment=info['System Platform X'])
        self._writer.output(name='System Memory', value=info['System Memory'], comment='MB')
        self._writer.output(name='System Swap Space',
                            value=info['System Swap Space'], comment='MB')
        self._writer.output(name='System Uptime', value=info['System Uptime'])
        self._writer.output(name='System Load', value=info['System Load'],
                            comment='average over last 1min, 5min & 15min')

    def _xwindows(self):
        xwininfo = syslib.Command('xwininfo', pathextra=['/usr/bin/X11', '/usr/openwin/bin'],
                                  args=['-root'], check=False)
        if xwininfo.is_found():
            xwininfo.run(mode='batch')
            if xwininfo.has_output():
                xset = syslib.Command('xset', pathextra=['/usr/bin/X11', '/usr/openwin/bin'],
                                      args=['-q'], check=False)
                if xset.is_found():
                    xset.run(mode='batch')
                    try:
                        for line in xset.get_output():
                            if 'Standby:' in line and 'Suspend:' in line and 'Off:' in line:
                                _, standby, _, suspend, _, off = (line + ' ').replace(
                                    ' 0 ', ' Off ').split()
                                self._writer.output(
                                    name='X-Display Power', value=standby + ' ' + suspend + ' ' +
                                    off, comment='DPMS Standby Suspend Off')
                                break
                        for line in xset.get_output():
                            if 'auto repeat delay:' in line and 'repeat rate:' in line:
                                self._writer.output(
                                    name='X-Keyboard Repeat', value=line.split()[3],
                                    comment=line.split()[6] + ' characters per second')
                                break
                        for line in xset.get_output():
                            if 'acceleration:' in line and 'threshold:' in line:
                                self._writer.output(
                                    name='X-Mouse Speed', value=line.split()[1],
                                    comment='acceleration factor')
                                break
                        for line in xset.get_output():
                            if 'timeout:' in line and 'cycle:' in line:
                                timeout = int(line.split()[1])
                                if timeout:
                                    self._writer.output(
                                        name='X-Screensaver', value=str(timeout),
                                        comment='no power saving for LCD but can keep CPU busy')
                                break
                    except (IndexError, ValueError):
                        pass

                xrandr = syslib.Command('xrandr', check=False)
                if xrandr.is_found():
                    xrandr.run(mode='batch')
                    for line in xrandr.get_output():
                        try:
                            if ' connected ' in line:
                                screen, _, resolution, *_, width, _, height = line.replace(
                                    'mm', '').split()
                                if width in ('0', '160') and height in ('0', '90'):
                                    self._writer.output(name="X-Windows Screen",
                                                        value=screen, comment=resolution)
                                else:
                                    size = math.sqrt(float(width)**2 + float(height)**2) / 25.4
                                    comment = '{0:s}, {1:s}mm x {2:s}mm, {3:3.1f}"'.format(
                                        resolution, width, height, size)
                                    self._writer.output(
                                        name='X-Windows Screen', value=screen, comment=comment)
                        except (IndexError, ValueError):
                            pass

                if 'DISPLAY' in os.environ:
                    width = '???'
                    height = '???'
                    try:
                        for line in xwininfo.get_output():
                            if 'Width:' in line:
                                width = line.split()[1]
                            elif 'Height:' in line:
                                height = line.split()[1]
                            elif 'Depth:' in line:
                                self._writer.output(name='X-Windows Server',
                                                    value=os.environ['DISPLAY'],
                                                    comment=width + 'x' + height + ', ' +
                                                    line.split()[1] + 'bit colour')
                    except IndexError:
                        pass

    def run(self):
        """
        Run detection
        """
        timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')
        print('\n' + self._author, '- System configuration detection tool')

        print('\n*** Detected at', timestamp, '***')
        self._network_information()
        self._operating_system()
        self._processors()
        self._system_status()
        if self._system.has_devices():
            self._system.detect_devices(self._writer)
        if self._system.has_loader():
            self._system.detect_loader(self._writer)
        self._xwindows()
        print()


class OperatingSystem(object):
    """
    Operating system class
    """

    def detect_loader(self, writer):
        """
        Detect loader
        """
        ldd = syslib.Command('ldd', args=['/bin/sh'], check=False)
        if ldd.is_found():
            ldd.run(filter='libc.*=>', mode='batch')
            if ldd.has_output():
                try:
                    glibc = ldd.get_output()[0].split()[2]
                    version = syslib.info.strings(glibc, 'GNU C Library').split(
                        'version')[1].replace(',', ' ').split()[0]
                except IndexError:
                    pass
                else:
                    writer.output(name='GNU C library', location=glibc, value=version)

        files = sorted(glob.glob('/lib*/ld*so.*'), reverse=True)
        loaders = []
        for file in files:
            if '/ld-linux' in file:
                loaders.append(file)
        if loaders:
            writer.output(name='Linux Loader', location=' '.join(loaders))

        for version in range(1, 10):
            loaders = []
            for file in files:
                if '/ld-lsb' in file and file.endswith('.so.' + str(version)):
                    loaders.append(file)
            if loaders:
                writer.output(name='LSB ' + str(version) + '.x Loader', location=' '.join(loaders))

    def has_devices(self):
        """
        Retrun False
        """
        return False

    def has_loader(self):
        """
        Return False
        """
        return False

    def get_fqdn(self):
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        fqdn = (socket.getfqdn()).lower()
        if fqdn.count('.') < 2:
            return 'Unknown'
        elif fqdn.endswith('.'):
            return fqdn
        else:
            return fqdn + '.'

    def get_net_info(self):
        """
        Return network information dictionary.
        """
        info = {}
        info['Net FQDN'] = self.get_fqdn()
        info['Net IPvx Address'] = []
        info['Net IPvx DNS'] = []
        return info

    def get_os_info(self):
        """
        Return operating system information dictionary.
        """
        info = {}
        info['OS Type'] = syslib.info.get_system()
        info['OS Name'] = 'Unknown'
        info['OS Kernel'] = 'Unknown'
        info['OS Kernel X'] = ''
        info['OS Patch'] = 'Unknown'
        info['OS Patch X'] = ''
        return info

    def get_cpu_info(self):
        """
        Return CPU information dictionary.
        """
        info = {}
        info['CPU Type'] = syslib.info.get_machine()
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
        if syslib.info.get_machine() == 'x86':
            info['CPU Type'] = 'x86'
        elif syslib.info.get_machine() == 'x86_64':
            info['CPU Type'] = 'x86'
        return info

    def get_sys_info(self):
        """
        Return system information dictionary.
        """
        info = {}
        info['System Platform'] = syslib.info.get_platform()
        info['System Platform X'] = ''
        info['System Memory'] = 'Unknown'
        info['System Swap Space'] = 'Unknown'
        info['System Uptime'] = 'Unknown'
        info['System Load'] = 'Unknown'
        return info

    def _has_value(self, values, word):
        for value in values.values():
            if word in str(value[0]):
                return True
        return False

    def _isitset(self, values, name):
        if name in values:
            return values[name][0]
        else:
            return 'Unknown'


class PosixSystem(OperatingSystem):
    """
    Posix system class
    """

    def detect_devices(self, writer):
        """
        Detect devices
        """
        mount = syslib.Command('mount', check=False)
        if mount.is_found():
            mount.run(filter=':', mode='batch')
            command = syslib.Command('df', flags=['-k'], check=False)
            for line in sorted(mount.get_output()):
                try:
                    device, _, directory = line.split()[:3]
                except IndexError:
                    continue
                size = '??? KB'
                if command.is_found():
                    command.set_args([directory])
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
                writer.output(name='Disk nfs', device='/dev/???', value=size,
                              comment=device + ' on ' + directory)

    def has_devices(self):
        return True

    def get_fqdn(self):
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        ispattern = re.compile(r'\s*(domain|search)\s')
        try:
            with open('/etc/resolv.conf', errors='replace') as ifile:
                for line in ifile:
                    if ispattern.match(line):
                        fqdn = syslib.info.get_hostname() + '.' + line.split()[1]
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
        info['OS Kernel'] = syslib.info.get_kernel()
        info['OS Kernel X'] = syslib.info.get_system()
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
        uptime = syslib.Command('uptime', check=False)
        if uptime.is_found():
            uptime.run(mode='batch')
            try:
                info['System Uptime'] = ','.join(uptime.get_output()[0].split(
                    ',')[:2]).split('up ')[1].strip()
                info['System Load'] = uptime.get_output()[0].split(': ')[-1]
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
        lspci = syslib.Command('lspci', pathextra=['/sbin'], args=['-k'], check=False)
        modinfo = syslib.Command('modinfo', pathextra=['/sbin'], check=False)
        if lspci.is_found():
            lspci.run(mode='batch')
            if not lspci.has_output():
                lspci.set_args([])
                lspci.run(mode='batch')
            for line in lspci.get_output():
                if 'Kernel driver in use:' in line:
                    driver = line.split()[-1]
                    if modinfo.is_found():
                        modinfo.set_args([driver])
                        modinfo.run(filter='^(version|vermagic):', mode='batch')
                        if modinfo.has_output():
                            self._devices[device] = (driver + ' driver ' +
                                                     modinfo.get_output()[0].split()[1])
                            continue
                elif not line.startswith('\t'):
                    device = line.replace('(', '').replace(')', '')
                    if 'VGA compatible controller: ' in line:
                        self._devices[device] = ''
                        if 'nvidia' in line.lower():
                            try:
                                with open('/proc/driver/nvidia/version', errors='replace') as ifile:
                                    for line in ifile:
                                        if 'Kernel Module ' in line:
                                            self._devices[device] = (
                                                'nvidia driver ' +
                                                line.split('Kernel Module ')[1].split()[0])
                            except OSError:
                                pass
                        elif 'VirtualBox' in line and modinfo.is_found():
                            modinfo.set_args(['vboxvideo'])
                            modinfo.run(filter='^(version|vermagic):', mode='batch')
                            if modinfo.has_output():
                                self._devices[device] = ('vboxvideo driver ' +
                                                         modinfo.get_output()[0].split()[1])
                                continue
                    else:
                        self._devices[device] = ''

    def _detect_audio(self, writer):
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
                for file in sorted(glob.glob('/proc/asound/card' + card + '/pcm*[cp]/info')):
                    try:
                        with open(file, errors='replace') as ifile:
                            for line in ifile:
                                if line.startswith('name: '):
                                    name = model + ' ' + line.rstrip(
                                        '\r\n').replace('name: ', '', 1)
                    except (IndexError, OSError):
                        continue
                    device = '/dev/snd/pcmC' + card + 'D' + os.path.dirname(file).split('pcm')[-1]
                    if os.path.exists(device):
                        if device.endswith('p'):
                            writer.output(name='Audio device', device=device, value=name,
                                          comment='SPK')
                        else:
                            writer.output(name='Audio device', device=device, value=name,
                                          comment='MIC')
                    else:
                        if card == '0':
                            unit = ''
                        else:
                            unit = card
                        if glob.glob('/proc/asound/card' + card + '/midi*'):
                            device = '/dev/midi' + unit
                            if not os.path.exists(device):
                                device = '/dev/???'
                            writer.output(name='Audio device', device=device, value=model,
                                          comment='MIDI')
                        device = '/dev/dsp' + unit
                        if not os.path.exists(device):
                            device = '/dev/???'
                        if glob.glob('/proc/asound/card' + card + '/pcm*c'):
                            if glob.glob('/proc/asound/card' + card + '/pcm*p'):
                                writer.output(name='Audio device', device=device, value=model,
                                              comment='MIC/SPK')
                            else:
                                writer.output(name='Audio device', device=device, value=model,
                                              comment='MIC')
                        elif glob.glob('/proc/asound/card' + card + '/pcm*p'):
                            writer.output(name='Audio device', device=device, value=model,
                                          comment='SPK')

    def _detect_battery(self, writer):
        batteries = ck_battery.Battery.factory()

        for battery in batteries:
            if battery.is_exist():
                model = (
                    battery.get_oem() + ' ' + battery.get_name() + ' ' + battery.get_type() + ' ' +
                    str(battery.get_capacity_max()) + 'mAh/' + str(battery.get_voltage()) + 'mV')
                if battery.get_charge() == '-':
                    state = '-'
                    if battery.get_rate() > 0:
                        state += str(battery.get_rate()) + 'mA'
                        if battery.get_voltage() > 0:
                            mywatts = '{0:4.2f}'.format(
                                float(battery.get_rate()*battery.get_voltage()) / 1000000)
                            state += ', ' + str(mywatts) + 'W'
                        hours = '{0:3.1f}'.format(
                            float(battery.get_capacity()) / battery.get_rate())
                        state += ', ' + str(hours) + 'h'
                elif battery.get_charge() == '+':
                    state = '+'
                    if battery.get_rate() > 0:
                        state += str(battery.get_rate()) + 'mA'
                        if battery.get_voltage() > 0:
                            mywatts = '{0:4.2f}'.format(
                                float(battery.get_rate() * battery.get_voltage()) / 1000000)
                            state += ', ' + str(mywatts) + 'W'
                else:
                    state = 'Unused'
                writer.output(name='Battery device', device='/dev/???',
                              value=str(battery.get_capacity()) + 'mAh',
                              comment=model + ' [' + state + ']')

    def _detect_cd(self, writer):
        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                with open(os.path.join(directory, 'driver'), errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('ide-cdrom '):
                            with open(os.path.join(directory, 'model'), errors='replace') as ifile:
                                model = ifile.readline().strip()
                                writer.output(name='CD device', device='/dev/' +
                                              os.path.basename(directory), value=model)
                                break
            except OSError:
                pass

        if os.path.isdir('/sys/bus/scsi/devices'):
            for file in sorted(glob.glob('/sys/block/sr*/device')):  # New kernels
                try:
                    identity = os.path.basename(os.readlink(file))
                except OSError:
                    continue
                try:
                    if os.path.isdir('/sys/bus/scsi/devices/' + identity):
                        with open(os.path.join('/sys/bus/scsi/devices', identity, 'vendor'),
                                  errors='replace') as ifile:
                            model = ifile.readline().strip()
                        with open(os.path.join('/sys/bus/scsi/devices', identity, 'model'),
                                  errors='replace') as ifile:
                            model += ' ' + ifile.readline().strip()
                except OSError:
                    model = '???'
                device = '/dev/' + os.path.basename(os.path.dirname(file))
                writer.output(name='CD device', device=device, value=model)
        else:
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
                            writer.output(name='CD device', device=device, value=model)
                            model = '???'
                            unit += 1
            except OSError:
                pass

    def _detect_disk(self, writer):
        swaps = []
        try:
            with open('/proc/swaps', errors='replace') as ifile:
                for line in ifile:
                    if line.startswith('/dev/'):
                        swaps.append(line.split()[0])
        except OSError:
            pass

        uuids = {}
        for file in glob.glob('/dev/disk/by-uuid/*'):
            try:
                uuids['/dev/' + os.path.basename(os.readlink(file))] = file
            except OSError:
                pass

        crypts = []
        lsblk = syslib.Command('lsblk', args=['-l'], check=False)
        if lsblk.is_found():
            lsblk.run(mode='batch')
            device = None
            for line in lsblk.get_output():
                if ' crypt ' in line:
                    crypts.append(device)
                    if '[SWAP]' in line:
                        swaps.append(device)
                    else:
                        uuids[device] = '/dev/mapper/' + line.split()[0]
                else:
                    device = '/dev/' + line.split()[0]

        mount = syslib.Command('mount', check=False)
        if mount.is_found():
            mount.run(filter='^/dev/', mode='batch')
        partitions = []
        try:
            with open('/proc/partitions', errors='replace') as ifile:
                for line in ifile:
                    partitions.append(line.rstrip('\r\n'))
        except OSError:
            pass

        for directory in sorted(glob.glob('/proc/ide/hd*')):
            try:
                with open(os.path.join(directory, 'driver'), errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('ide-disk '):
                            with open(os.path.join(directory, 'model'), errors='replace') as ifile2:
                                model = ifile2.readline().rstrip('\r\n')
                            hdx = os.path.basename(directory)
                            for partition in partitions:
                                if partition.endswith(hdx) or hdx + ' ' in partition:
                                    try:
                                        size = partition.split()[2]
                                    except IndexError:
                                        size = '???'
                                    writer.output(name='Disk device', device='/dev/' + hdx,
                                                  value=size + ' KB', comment=model)
                                elif hdx in partition:
                                    size, hdxn = partition.split()[2:4]
                                    device = '/dev/' + hdxn
                                    comment = ''
                                    if device in swaps:
                                        comment = 'swap'
                                    else:
                                        for line2 in mount.get_output():
                                            if line2.startswith(device + ' '):
                                                try:
                                                    mount_point, _, mount_type = line2.split()[2:]
                                                    comment = mount_type + ' on ' + mount_point
                                                except (IndexError, ValueError):
                                                    comment = '??? on ???'
                                                break
                                    writer.output(name='Disk device', device=device,
                                                  value=size + ' KB', comment=comment)
            except OSError:
                pass

        if os.path.isdir('/sys/bus/scsi/devices'):
            for file in sorted(glob.glob('/sys/block/sd*/device')):  # New kernels
                try:
                    identity = os.path.basename(os.readlink(file))
                except OSError:
                    continue
                try:
                    if os.path.isdir('/sys/bus/scsi/devices/' + identity):
                        with open(os.path.join('/sys/bus/scsi/devices', identity, 'vendor'),
                                  errors='replace') as ifile:
                            model = ifile.readline().strip()
                        with open(os.path.join('/sys/bus/scsi/devices', identity, 'model'),
                                  errors='replace') as ifile:
                            model += ' ' + ifile.readline().strip()
                except OSError:
                    model = '???'
                sdx = os.path.basename(os.path.dirname(file))
                for partition in partitions:
                    if partition.endswith(sdx) or sdx + ' ' in partition:
                        try:
                            size = partition.split()[2]
                        except IndexError:
                            size = '???'
                        writer.output(name='Disk device', device='/dev/' + sdx, value=size + ' KB',
                                      comment=model)
                    elif sdx in partition:
                        size, sdxn = partition.split()[2:4]
                        device = '/dev/' + sdxn
                        comment = ''
                        if device in swaps:
                            comment = 'swap'
                        else:
                            for line2 in mount.get_output():
                                try:
                                    if (line2.startswith(device + ' ') or
                                            line2.startswith(uuids[device] + ' ')):
                                        try:
                                            mount_point, _, mount_type = line2.split()[2:]
                                            comment = mount_type + ' on ' + mount_point
                                        except (IndexError, ValueError):
                                            comment = '??? on ???'
                                        break
                                except KeyError:
                                    pass
                        if device in crypts:
                            comment = 'crypt:' + comment
                        writer.output(name='Disk device', device=device, value=size + ' KB',
                                      comment=comment)
        else:
            model = '???'
            unit = 0
            isjunk = re.compile('.*Vendor: | *Model:| *Rev: .*')
            try:
                with open('/proc/scsi/scsi', errors='replace') as ifile:
                    for line in ifile:
                        if 'Vendor: ' in line and 'Model: ' in line:
                            model = isjunk.sub('', line.rstrip('\r\n'))
                        elif 'Type:' in line and 'Direct-Access' in line:
                            sdx = 'sd' + chr(97 + unit)
                            if os.path.exists('/dev/' + sdx):
                                for partition in partitions:
                                    if partition.endswith(sdx) or sdx + ' ' in partition:
                                        try:
                                            size = partition.split()[2]
                                        except IndexError:
                                            size = '???'
                                        writer.output(name='Disk device', device='/dev/' + sdx,
                                                      value=size + ' KB', comment=model)
                                    elif sdx in partition:
                                        size, sdxn = partition.split()[2:4]
                                        device = '/dev/' + sdxn
                                        comment = ''
                                        if device in swaps:
                                            comment = 'swap'
                                        else:
                                            for line2 in mount.get_output():
                                                if line2.startswith(device + ' '):
                                                    try:
                                                        mount_point, _, mount_type = line2.split(
                                                            )[2:]
                                                        comment = mount_type + ' on ' + mount_point
                                                    except (IndexError, ValueError):
                                                        comment = '??? on ???'
                                                    break
                                        writer.output(name='Disk device', device=device,
                                                      value=size + ' KB', comment=comment)
                            model = '???'
                            unit += 1
            except OSError:
                pass

    def _detect_ethernet(self, writer):
        # Ethernet device detection
        for line, device in sorted(self._devices.items()):
            if 'Ethernet controller: ' in line:
                model = line.split('Ethernet controller: ')[1].replace(
                    'Semiconductor ', '').replace('Co., ', '').replace(
                        'Ltd. ', '').replace('PCI Express ', '')
                writer.output(name='Ethernet device', device='/dev/???', value=model,
                              comment=device)

    def _detect_firewire(self, writer):
        for line, device in sorted(self._devices.items()):
            if 'FireWire (IEEE 1394): ' in line:
                model = line.split('FireWire (IEEE 1394): ')[1]
                writer.output(name='Firewire device', device='/dev/???', value=model,
                              comment=device)

    def _detect_graphics(self, writer):
        for line, device in sorted(self._devices.items()):
            if 'VGA compatible controller: ' in line:
                model = line.split('VGA compatible controller: ')[1].strip()
                writer.output(name='Graphics device', device='/dev/???', value=model,
                              comment=device)

    def _detect_inifiniband(self, writer):
        for line, device in sorted(self._devices.items()):
            if 'InfiniBand: ' in line:
                model = line.split('InfiniBand: ')[1].replace('InfiniHost', 'InifiniBand')
                writer.output(name='InifiniBand device', device='/dev/???', value=model,
                              comment=device)

    def _detect_input(self, writer):
        info = {}
        for file in glob.glob('/dev/input/by-path/*event*'):
            try:
                device = '/dev/input/' + os.path.basename(os.readlink(file))
                if os.path.exists(device):
                    info[device] = os.path.basename(file).replace('-event', '').replace('-', ' ')
            except OSError:
                continue

        isjunk = re.compile(r'/usb-\w{4}_\w{4}-')
        for file in glob.glob('/dev/input/by-id/*event*'):
            try:
                device = '/dev/input/' + os.path.basename(os.readlink(file))
                if os.path.exists(device) and not isjunk.search(file):
                    info[device] = os.path.basename(file).split('-')[1].replace('_', ' ')
            except (IndexError, OSError):
                continue
        for key, value in sorted(info.items()):
            writer.output(name='Input device', device=key, value=value)

    def _detect_network(self, writer):
        for line, device in sorted(self._devices.items()):
            if 'Network controller: ' in line:
                model = line.split(': ', 1)[1].split(' (')[0]
                writer.output(name='Network device', device='/dev/???', value=model,
                              comment=device)

    def _detect_video(self, writer):
        for directory in sorted(glob.glob('/sys/class/video4linux/*')):
            device = os.path.basename(directory)
            try:
                with open(os.path.join(directory, 'name'), errors='replace') as ifile:
                    writer.output(name='Video device', device='/dev/' + device,
                                  value=ifile.readline().rstrip('\r\n'))
                    continue
            except OSError:
                pass
            writer.output(name='Video device', device='/dev/' + device, value='???')

    def detect_devices(self, writer):
        """
        Detect devices
        """
        self._detect_audio(writer)
        self._detect_battery(writer)
        self._detect_cd(writer)
        self._detect_disk(writer)

        # Disk mounts detection
        super().detect_devices(writer)

        self._detect_ethernet(writer)
        self._detect_firewire(writer)
        self._detect_graphics(writer)
        self._detect_inifiniband(writer)
        self._detect_input(writer)
        self._detect_network(writer)
        self._detect_video(writer)

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
        if 'LANG' not in os.environ:
            env['LANG'] = 'en_US'
        ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
        ifconfig.run(env=env, filter='inet[6]? addr', mode='batch')
        isjunk = re.compile('.*inet[6]? addr[a-z]*:')
        for line in ifconfig.get_output():
            info['Net IPvx Address'].append(isjunk.sub(' ', line).split()[0])
        return info

    def get_os_info(self):
        """
        Return operating system information dictionary.
        """
        info = super().get_os_info()
        if os.path.isfile('/etc/redhat-release'):
            try:
                with open('/etc/redhat-release', errors='replace') as ifile:
                    info['OS Name'] = ifile.readline().rstrip('\r\n')
            except OSError:
                pass
            return info
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
                return info
            except OSError:
                info['OS Name'] = 'Unknown'
            return info
        elif os.path.isfile('/etc/lsb-release'):
            try:
                with open('/etc/lsb-release', errors='replace') as ifile:
                    lines = []
                    for line in ifile:
                        lines.append(line.rstrip('\r\n'))
            except OSError:
                pass
            else:
                if lines and lines[-1].startswith('DISTRIB_DESCRIPTION='):
                    info['OS Name'] = lines[-1].split('=')[1].replace("'", '')
                    return info
                else:
                    identity = None
                    for line in lines:
                        if line.startswith('DISTRIB_ID='):
                            identity = line.split('=')[1]
                        elif line.startswith('DISTRIB_RELEASE=') and identity:
                            info['OS Name'] = identity + ' ' + line.split('=')[1]
                            return info
        if os.path.isfile('/etc/kanotix-version'):
            try:
                with open('/etc/kanotix-version', errors='replace') as ifile:
                    info['OS Name'] = 'Kanotix ' + ifile.readline().rstrip('\r\n').split()[1]
            except (IndexError, OSError):
                pass
            return info
        elif os.path.isfile('/etc/knoppix-version'):
            try:
                with open('/etc/knoppix-version', errors='replace') as ifile:
                    info['OS Name'] = 'Knoppix ' + ifile.readline().rstrip('\r\n').split()[0]
            except (IndexError, OSError):
                pass
            return info
        elif os.path.isfile('/etc/debian_version'):
            try:
                with open('/etc/debian_version', errors='replace') as ifile:
                    info['OS Name'] = 'Debian ' + ifile.readline().rstrip(
                        '\r\n').split('=')[-1].replace("'", '')
            except OSError:
                pass
            return info
        elif os.path.isfile('/etc/DISTRO_SPECS'):
            try:
                identity = None
                with open('/etc/DISTRO_SPECS', errors='replace') as ifile:
                    for line in ifile:
                        if line.startswith('DISTRO_NAME'):
                            identity = line.rstrip('\r\n').split('=')[1].replace('"', '')
                        elif line.startswith('DISTRO_VERSION') and identity:
                            info['OS Name'] = identity + ' ' + line.rstrip('\r\n').split('=')[1]
                            return info
            except (IndexError, OSError):
                pass
            return info
        dpkg = syslib.Command('dpkg', check=False, args=['--list'])
        if dpkg.is_found():
            dpkg.run(mode='batch')
            for line in dpkg.get_output():
                try:
                    package = line.split()[1]
                    if package == 'knoppix-g':
                        info['OS Name'] = 'Knoppix ' + line.split()[2].split('-')[0]
                        return info
                    elif package == 'mepis-auto':
                        info['OS Name'] = 'MEPIS ' + line.split()[2]
                        return info
                    elif ' kernel ' in line and 'MEPIS' in line:
                        isjunk = re.compile('MEPIS.')
                        info['OS Name'] = 'MEPIS ' + isjunk.sub('', line.split()[2])
                        return info
                except IndexError:
                    pass
            for line in dpkg.get_output():
                try:
                    package = line.split()[1]
                    if package == 'base-files':
                        info['OS Name'] = 'Debian ' + line.split()[2]
                        return info
                except IndexError:
                    pass
            return info
        return info

    def get_cpu_info(self):
        """
        Return CPU information dictionary.
        """
        info = super().get_cpu_info()
        isspace = re.compile(r'\s+')

        if info['CPU Addressability'] == 'Unknown':
            if syslib.info.get_machine().endswith('64'):
                info['CPU Addressability'] = '64bit'
            else:
                info['CPU Addressability'] = '32bit'

        try:
            with open('/proc/cpuinfo', errors='replace') as ifile:
                lines = []
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except OSError:
            pass
        try:
            if syslib.info.get_machine() == 'Power':
                for line in lines:
                    if line.startswith('cpu'):
                        info['CPU Model'] = 'PowerPC_' + isspace.sub(
                            ' ', line.split(': ')[1].split(' ')[0].strip())
                        break
            if info['CPU Model'] == 'Unknown':
                for line in lines:
                    if line.startswith('model name'):
                        info['CPU Model'] = isspace.sub(' ', line.split(': ')[1].strip())
                        break
            if syslib.info.get_machine() == 'x86_64':
                for line in lines:
                    if line.startswith('address size'):
                        info['CPU Addressability X'] = line.split(
                            ':')[1].split()[0] + 'bit physical'
        except (IndexError, OSError):
            pass

        try:
            threads = len(glob.glob('/sys/devices/system/cpu/cpu[0-9]*'))
        except (IndexError, ValueError):
            threads = 0
        if not threads:
            for line in lines:
                if line.startswith('processor'):
                    threads += 1

        vitual_machine = self._get_virtual_machine()
        if vitual_machine:
            info['CPU Cores'] = str(threads)
            info['CPU Cores X'] = vitual_machine + ' VM'
            info['CPU Threads'] = info['CPU Cores']
            info['CPU Threads X'] = info['CPU Cores X']
        else:
            found = []
            for file in glob.glob('/sys/devices/system/cpu/cpu[0-9]*/topology/physical_package_id'):
                try:
                    with open(file, errors='replace') as ifile:
                        line = ifile.readline().rstrip('\r\n')
                        if line not in found:
                            found.append(line)
                except OSError:
                    pass
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
            try:
                with open('/sys/devices/system/cpu/cpu0/topology/thread_siblings_list',
                          errors='replace') as ifile:
                    cpu_cores = int(threads/(int(ifile.readline().rstrip(
                        '\r\n').split('-')[-1]) + 1))
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
            info['CPU Sockets'] = str(sockets)
            info['CPU Cores'] = str(cpu_cores)
            info['CPU Threads'] = str(threads)
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq',
                      errors='replace') as ifile:
                info['CPU Clock'] = str(int(int(ifile.readline().rstrip('\r\n')) / 1000 + 0.5))
        except (OSError, ValueError):
            for line in lines:
                if line.startswith('cpu MHz'):
                    try:
                        info['CPU Clock'] = str(int(float(line.split(': ')[1]) + 0.5))
                    except (IndexError, ValueError):
                        pass
                    break
            if info['CPU Clock'] == 'Unknown':
                for line in lines:
                    if line.startswith('clock'):
                        try:
                            info['CPU Clock'] = str(int(float(line.split(': ')[1]) + 0.5))
                        except (IndexError, ValueError):
                            pass
                        break
        found = []
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies',
                      errors='replace') as ifile:
                for clock in ifile.readline().rstrip('\r\n').split():
                    found.append(str(int(int(clock) / 1000 + 0.5)))
                if found:
                    info['CPU Clocks'] = ' '.join(found)
        except (OSError, ValueError):
            try:
                with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq',
                          errors='replace') as ifile:
                    info['CPU Clocks'] = str(int(int(ifile.readline()) / 1000 + 0.5))
                with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq',
                          errors='replace') as ifile:
                    info['CPU Clocks'] += ' ' + str(int(int(ifile.readline()) / 1000 + 0.5))
            except (OSError, ValueError):
                info['CPU Clocks'] = 'Unknown'
        for cache in sorted(glob.glob('/sys/devices/system/cpu/cpu0/cache/index*')):
            try:
                with open(os.path.join(cache, 'level'), errors='replace') as ifile:
                    level = ifile.readline().rstrip('\r\n')
                with open(os.path.join(cache, 'type'), errors='replace') as ifile:
                    type_ = ifile.readline().rstrip('\r\n')
                if type_ == 'Data':
                    level += 'd'
                elif type_ == 'Instruction':
                    level += 'i'
                with open(os.path.join(cache, 'size'), errors='replace') as ifile:
                    info['CPU Cache'][level] = str(int(ifile.readline().rstrip('\r\nK')))
            except (OSError, ValueError):
                pass
        if not info['CPU Cache']:
            for line in lines:
                if line.startswith('cache size'):
                    try:
                        info['CPU Cache']['?'] = str(int(float(line.split()[3])))
                    except (IndexError, ValueError):
                        pass
                    break
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
                            info['System Memory'] = str(int(float(line.split()[1]) / 1024 + 0.5))
                        elif line.startswith('SwapTotal:'):
                            info['System Swap Space'] = str(int(float(line.split()[1]) /
                                                                1024 + 0.5))
                except (IndexError, ValueError):
                    pass
        except OSError:
            pass
        return info

    def _get_virtual_machine(self):
        if os.path.isdir('/sys/devices/xen'):
            return 'Xen'

        for line in self._devices:
            if 'RHEV' in line:
                return 'RHEV'
            elif 'VirtualBox' in line:
                return 'VirtualBox'
            elif 'VMWare' in line or 'VMware' in line:
                return 'VMware'
            elif ' Xen ' in line in line:
                return 'Xen'

        for file in (glob.glob('/sys/bus/scsi/devices/*/model') + ['/proc/scsi/scsi'] +
                     glob.glob('/proc/ide/hd?/model')):
            try:
                with open(file, errors='replace') as ifile:
                    for line in ifile:
                        if 'RHEV' in line:
                            return 'RHEV'
                        elif 'VBOX ' in line:
                            return 'VirtualBox'
                        elif 'VMWare ' in line or 'VMware ' in line:
                            return 'VMware'
            except OSError:
                pass
        return None


class WindowsSystem(OperatingSystem):
    """
    Windows system class
    """

    def __init__(self):
        pathextra = []
        if 'WINDIR' in os.environ:
            pathextra.append(os.path.join(os.environ['WINDIR'], 'system32'))
        self._ipconfig = syslib.Command('ipconfig', pathextra=pathextra, args=['-all'])
        # Except for WIndows XP Home
        self._systeminfo = syslib.Command('systeminfo', pathextra=pathextra, check=False)

    def get_fqdn(self):
        """
        Return fully qualified domain name (ie 'hostname.domain.com.').
        """
        if not self._ipconfig.has_output():
            self._ipconfig.run(mode='batch')
        for line in self._ipconfig.get_output('Connection-specific DNS Suffix'):
            fqdn = syslib.info.get_hostname() + '.' + line.split()[-1]
            if fqdn.count('.') > 1:
                if fqdn.endswith('.'):
                    return fqdn
                return fqdn + '.'
        return super().get_fqdn()

    def get_net_info(self):
        """
        Return network information dictionary.
        """
        info = {}
        info['Net FQDN'] = self.get_fqdn()
        if not self._ipconfig.has_output():
            self._ipconfig.run(mode='batch')
        info['Net IPvx Address'] = []
        for line in self._ipconfig.get_output('IP.* Address'):
            (info['Net IPvx Address']).append(line.replace('(Preferred)', '').split()[-1])
        info['Net IPvx DNS'] = []
        for line in self._ipconfig.get_output():
            if 'DNS Servers' in line:
                (info['Net IPvx DNS']).append(line.split()[-1])
            elif info['Net IPvx DNS']:
                if ' : ' in line:
                    break
                (info['Net IPvx DNS']).append(line.split()[-1])
        return info

    def get_os_info(self):
        """
        Return operating system information dictionary.
        """
        info = {}
        info['OS Type'] = 'windows'
        info['OS Kernel X'] = 'NT'
        values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')[1]
        info['OS Name'] = self._isitset(values, 'ProductName')
        info['OS Kernel'] = syslib.info.get_kernel()
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
        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor')
        info['CPU Cores'] = str(len(subkeys))
        info['CPU Threads'] = info['CPU Cores']
        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\BIOS')
        if self._systeminfo.is_found():
            self._systeminfo.run(mode='batch')
        if self._has_value(values, 'RHEV') or self._systeminfo.is_match_output('RHEV'):
            info['CPU Cores X'] = 'RHEV VM'
        elif self._has_value(values, 'VMware') or self._systeminfo.is_match_output('VMware'):
            info['CPU Cores X'] = 'VMware VM'
        elif (self._has_value(values, 'VirtualBox') or
              self._systeminfo.is_match_output('VirtualBox')):
            info['CPU Cores X'] = 'VirtualBox VM'
        subkeys, values = self._reg_read(
            winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')
        info['CPU Model'] = re.sub(' +', ' ', self._isitset(values, 'ProcessorNameString').strip())
        info['CPU Clock'] = str(self._isitset(values, '~MHz'))
        return info

    def get_sys_info(self):
        """
        Return system information dictionary.
        """
        info = super().get_sys_info()
        if self._systeminfo.is_found():
            self._systeminfo.run(mode='batch')
        memory = self._systeminfo.get_output(':.*MB$')
        if len(memory) > 0:
            info['System Memory'] = memory[0].split()[-2].replace(',', '')
        if len(memory) > 2:
            info['System Swap Space'] = memory[4].split()[-2].replace(',', '')
        try:
            uptime = self._systeminfo.get_output('^System Up Time:')[0].split()
            info['System Uptime'] = (uptime[3] + ' days ' + uptime[5].zfill(2) +
                                     ':' + uptime[7].zfill(2))
        except IndexError:
            pass
        info['System Load'] = 'Unknown'
        return info

    def _reg_read(self, hive, path):
        subkeys = []
        values = {}
        try:
            key = winreg.OpenKey(hive, path)
        except WindowsError:
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

    def __init__(self, options):
        self._options = options

    def output(self, name, architecture='', comment='', device='', location='', value=''):
        """
        Output information
        """
        line = ' {0:19s}'.format(name + ':')
        if device:
            line += (' {0:12s}'.format(device)) + ' ' + value
        elif location:
            line += ' ' + location
            if value:
                line += '  ' + value
        elif value:
            line += ' ' + value
        if architecture:
            line += ' (' + architecture + ')'
        if comment:
            line += ' (' + comment + ')'
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
        except (syslib.SyslibError, SystemExit) as exception:
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

        try:
            Detect(options).run()
        except syslib.SyslibError as exception:
            raise SystemExit(exception)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
