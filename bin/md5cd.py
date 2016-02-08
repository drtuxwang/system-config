#!/usr/bin/env python3
"""
Calculate MD5 checksums for CD/DVD data disk.
"""

import argparse
import glob
import hashlib
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_device(self):
        """
        Return device location.
        """
        return self._args.device[0]

    def get_speed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Calculate MD5 checksums for CD/DVD data disk.')

        parser.add_argument('-speed', nargs=1, type=int, default=[8],
                            help='Select CD/DVD spin speed.')

        parser.add_argument('device', nargs=1, metavar='device|scan',
                            help='CD/DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        os.umask(int('077', 8))

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'CD/DVD device speed.')
        if self._args.device[0] != 'scan' and not os.path.exists(self._args.device[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] + '" CD/DVD device.')


class Cdrom(object):
    """
    CDROM class
    """

    def __init__(self):
        self._devices = {}
        self.detect()

    def get_devices(self):
        """
        Return list of devices
        """
        return self._devices

    def detect(self):
        """
        Detect devices
        """
        for directory in glob.glob('/sys/block/sr*/device'):
            device = '/dev/' + os.path.basename(os.path.dirname(directory))
            model = ''
            for file in ('vendor', 'model'):
                try:
                    with open(os.path.join(directory, file), errors='replace') as ifile:
                        model += ' ' + ifile.readline().strip()
                except OSError:
                    continue
            self._devices[device] = model


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

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _cdspeed(device, speed):
        cdspeed = syslib.Command('cdspeed', flags=[device], check=False)
        if cdspeed.is_found():
            if speed:
                cdspeed.set_args([str(speed)])
            # If CD/DVD spin speed change fails its okay
            cdspeed.run()
        elif speed:
            hdparm = syslib.Command(file='/sbin/hdparm', args=['-E', str(speed), device])
            hdparm.run(mode='batch')

    @staticmethod
    def _md5tao(device):
        isoinfo = syslib.Command('isoinfo')
        nice = syslib.Command('nice', args=['-20'])
        tmpfile = os.sep + os.path.join(
            'tmp', 'fprint-' + syslib.info.get_username() + '.' + str(os.getpid()))
        command = syslib.Command(
            'dd', args=['if=' + device, 'bs=' + str(2048*4096), 'count=1', 'of=' + tmpfile])
        command.run(mode='batch')
        if command.get_error('Permission denied$'):
            raise SystemExit(sys.argv[0] +
                             ': Cannot read from CD/DVD device. Please check permissions.')
        elif not os.path.isfile(tmpfile):
            raise SystemExit(sys.argv[0] + ': Cannot find CD/DVD media. Please check drive.')

        isoinfo.set_args(['-d', '-i', tmpfile])
        isoinfo.run(filter='^Volume size is: ', mode='batch')
        if not isoinfo.has_output():
            raise SystemExit(sys.argv[0] +
                             ': Cannot find TOC on CD/DVD media. Disk not recognised.')
        elif isoinfo.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(isoinfo.get_exitcode()) +
                             ' received from "' + isoinfo.get_file() + '".')
        blocks = int(isoinfo.get_output()[0].split()[-1])

        command.set_args(['if=' + device, 'bs=2048', 'count=' + str(blocks)])
        command.set_wrapper(nice)
        child = command.run(mode='child')
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
        if eject.is_found():
            eject.run(mode='batch')
            if eject.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(eject.get_exitcode()) +
                                 ' received from "' + eject.get_file() + '".')

    @staticmethod
    def _scan():
        cdrom = Cdrom()
        print('Scanning for CD/DVD devices...')
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print('  {0:10s}  {1:s}'.format(key, value))

    def run(self):
        """
        Start program
        """
        options = Options()

        device = options.get_device()

        if device == 'scan':
            self._scan()
        else:
            self._cdspeed(device, options.get_speed())
            self._md5tao(device)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
