#!/usr/bin/env python3
"""
Rip Video DVD title to file.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._vlc = syslib.Command('vlc')

    def get_device(self):
        """
        Return device location.
        """
        return self._args.device[0]

    def get_vlc(self):
        """
        Return vlc Command class object.
        """
        return self._vlc

    def get_speed(self):
        """
        Return DVD speed.
        """
        return self._args.speed[0]

    def get_title(self):
        """
        Return DVD title.
        """
        return self._args.title[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Rip Video DVD title to file.')

        parser.add_argument('-speed', nargs=1, type=int, default=[8],
                            help='Select DVD spin speed.')
        parser.add_argument('-title', nargs=1, type=int, default=[1],
                            help='Select DVD title to rip (Default is 1).')

        parser.add_argument(
            'device', nargs=1, metavar='device|scan', help='DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'DVD device speed.')
        if self._args.title[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for DVD title.')
        if self._args.device[0] != 'scan' and not os.path.exists(self._args.device[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] + '" DVD device.')


class Cdrom(object):
    """
    CDROM class
    """

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

    def get_devices(self):
        """
        Return list of devices
        """
        return self._devices


class RipDvd(object):
    """
    Rip DVD class
    """

    def __init__(self, options):
        self._vlc = options.get_vlc()
        self._device = options.get_device()
        self._speed = options.get_speed()
        self._title = options.get_title()

        if self._device == 'scan':
            self._scan()
        else:
            self._cdspeed(self._device, options.get_speed())
            self._rip(options)

    def _cdspeed(self, device, speed):
        cdspeed = syslib.Command('cdspeed', flags=[device], check=False)
        if cdspeed.is_found():
            if speed:
                cdspeed.set_args([str(speed)])
            # If CD/DVD spin speed change fails its okay
            cdspeed.run()
        elif speed:
            hdparm = syslib.Command(file='/sbin/hdparm', args=['-E', str(speed), device])
            hdparm.run(mode='batch')

    def _rip(self, options):
        file = 'title-' + str(self._title).zfill(2) + '.mpg'
        self._vlc.set_args(
            ['dvdsimple:/' + self._device + ':#' + str(self._title), '--sout',
             '#standard{access=file,mux=ts,dst=' + file + '}', 'vlc://quit'])
        self._vlc.run()

    def _scan(self):
        cdrom = Cdrom()
        print('Scanning for CD/DVD devices...')
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print('  {0:10s}  {1:s}'.format(key, value))


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
            RipDvd(options)
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
