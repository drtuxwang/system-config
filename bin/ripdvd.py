#!/usr/bin/env python3
"""
Rip Video DVD title to file.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Options:
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
        parser = argparse.ArgumentParser(
            description='Rip Video DVD title to file.')

        parser.add_argument(
            '-speed',
            nargs=1,
            type=int,
            default=[8],
            help='Select DVD spin speed.'
        )
        parser.add_argument(
            '-title',
            nargs=1,
            type=int,
            default=[1],
            help='Select DVD title to rip (Default is 1).'
        )
        parser.add_argument(
            'device',
            nargs=1,
            metavar='device|scan',
            help='DVD device (ie "/dev/sr0" or "scan".'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._vlc = command_mod.Command('vlc', errors='stop')

        if self._args.speed[0] < 1:
            raise SystemExit(
                sys.argv[0] +
                ': You must specific a positive integer for DVD device speed.'
            )
        if self._args.title[0] < 1:
            raise SystemExit(
                sys.argv[0] +
                ': You must specific a positive integer for DVD title.'
            )
        if (
                self._args.device[0] != 'scan' and
                not os.path.exists(self._args.device[0])
        ):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] +
                '" DVD device.'
            )


class Cdrom:
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
                    with open(
                            os.path.join(directory, file),
                            errors='replace'
                    ) as ifile:
                        model += ' ' + ifile.readline().strip()
                except OSError:
                    continue
            self._devices[device] = model


class Main:
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
        cdspeed = command_mod.Command('cdspeed', errors='ignore')
        if cdspeed.is_found():
            if speed:
                cdspeed.set_args([device, str(speed)])
            # If CD/DVD spin speed change fails its okay
            subtask_mod.Task(cdspeed.get_cmdline()).run()
        elif speed and os.path.isfile('/sbin/hdparm'):
            hdparm = command_mod.Command('/sbin/hdparm', errors='ignore')
            hdparm.set_args(['-E', str(speed), device])
            subtask_mod.Batch(hdparm.get_cmdline()).run()

    def _rip(self):
        file = 'title-' + str(self._title).zfill(2) + '.mpg'
        self._vlc.set_args(
            ['dvdsimple:/' + self._device + ':#' + str(self._title), '--sout',
             '#standard{access=file,mux=ts,dst=' + file + '}', 'vlc://quit'])
        subtask_mod.Task(self._vlc.get_cmdline()).run()

    @staticmethod
    def _scan():
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print("  {0:10s}  {1:s}".format(key, value))

    def run(self):
        """
        Start program
        """
        options = Options()

        self._vlc = options.get_vlc()
        self._device = options.get_device()
        self._speed = options.get_speed()
        self._title = options.get_title()

        if self._device == 'scan':
            self._scan()
        else:
            self._cdspeed(self._device, options.get_speed())
            self._rip()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
