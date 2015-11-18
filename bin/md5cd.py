#!/usr/bin/env python3
"""
Calculate MD5 checksums for CD/DVD data disk.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import hashlib
import os
import signal
import time

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        os.umask(int('077', 8))

    def getDevice(self):
        """
        Return device location.
        """
        return self._args.device[0]

    def getSpeed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Calculate MD5 checksums for CD/DVD data disk.')

        parser.add_argument('-speed', nargs=1, type=int, default=[8],
                            help='Select CD/DVD spin speed.')

        parser.add_argument('device', nargs=1, metavar='device|scan',
                            help='CD/DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'CD/DVD device speed.')
        if self._args.device[0] != 'scan' and not os.path.exists(self._args.device[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] + '" CD/DVD device.')


class Cdrom:

    def __init__(self):
        self._devices = {}
        for directory in glob.glob('/sys/block/sr*/device'):
            device = '/dev/' + os.path.basename(os.path.dirname(directory))
            model = ''
            for file in ('vendor', 'model'):
                try:
                    with open(os.path.join(directory, file), errors='replace') as ifile:
                        model += ' ' + ifile.readline().strip()
                except IOError:
                    continue
            self._devices[device] = model

    def device(self, mount):
        if mount == 'cdrom':
            rank = 0
        else:
            try:
                rank = int(mount[5:])-1
            except ValueError:
                return ''
        try:
            return sorted(self._devices.keys())[rank]
        except IndexError:
            return ''

    def getDevices(self):
        """
        Return list of devices
        """
        return self._devices


class Md5cd:

    def __init__(self, options):
        device = options.getDevice()

        if device == 'scan':
            self._scan()
        else:
            self._cdspeed(device, options.getSpeed())
            self._md5tao(device)

    def _cdspeed(self, device, speed):
        cdspeed = syslib.Command('cdspeed', flags=[device], check=False)
        if cdspeed.isFound():
            if speed:
                cdspeed.setArgs([str(speed)])
            # If CD/DVD spin speed change fails its okay
            cdspeed.run()
        elif speed:
            hdparm = syslib.Command(file='/sbin/hdparm', args=['-E', str(speed), device])
            hdparm.run(mode='batch')

    def _md5tao(self, device):
        isoinfo = syslib.Command('isoinfo')
        nice = syslib.Command('nice', args=['-20'])
        tmpfile = os.sep + os.path.join(
            'tmp', 'fprint-' + syslib.info.getUsername() + '.' + str(os.getpid()))
        dd = syslib.Command(
            'dd', args=['if=' + device, 'bs=' + str(2048*4096), 'count=1', 'of=' + tmpfile])
        dd.run(mode='batch')
        if dd.getError('Permission denied$'):
            raise SystemExit(sys.argv[0] +
                             ': Cannot read from CD/DVD device. Please check permissions.')
        elif not os.path.isfile(tmpfile):
            raise SystemExit(sys.argv[0] + ': Cannot find CD/DVD media. Please check drive.')

        isoinfo.setArgs(['-d', '-i', tmpfile])
        isoinfo.run(filter='^Volume size is: ', mode='batch')
        if not isoinfo.hasOutput():
            raise SystemExit(sys.argv[0] +
                             ': Cannot find TOC on CD/DVD media. Disk not recognised.')
        elif isoinfo.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(isoinfo.getExitcode()) +
                             ' received from "' + isoinfo.getFile() + '".')
        blocks = int(isoinfo.getOutput()[0].split()[-1])

        dd.setArgs(['if=' + device, 'bs=2048', 'count=' + str(blocks)])
        dd.setWrapper(nice)
        child = dd.run(mode='child')
        child.stdin.close()
        size = 0
        md5 = hashlib.md5()

        while True:
            chunk = child.stdout.read(131072)
            if not chunk:
                break
            md5.update(chunk)
            size += len(chunk)
        pad = int(blocks * 2048 - size)
        if pad > 0 and pad < 16777216:
            md5.update(b'\0'*pad)  # Padding
        print(md5.hexdigest(), device, sep='  ')
        time.sleep(1)

        eject = syslib.Command('eject', check=False)
        if eject.isFound():
            eject.run(mode='batch')
            if eject.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(eject.getExitcode()) +
                                 ' received from "' + eject.getFile() + '".')

    def _scan(self):
        cdrom = Cdrom()
        print('Scanning for CD/DVD devices...')
        devices = cdrom.getDevices()
        for key, value in sorted(devices.items()):
            print('  {0:10s}  {1:s}'.format(key, value))


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Md5cd(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
