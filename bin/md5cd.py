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
from typing import List

import command_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_device(self) -> str:
        """
        Return device location.
        """
        return self._args.device[0]

    def get_speed(self) -> int:
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Calculate MD5 checksums for CD/DVD data disk.',
        )

        parser.add_argument(
            '-speed',
            nargs=1,
            type=int,
            default=[8],
            help='Select CD/DVD spin speed.'
        )
        parser.add_argument(
            'device',
            nargs=1,
            metavar='device|scan',
            help='CD/DVD device (ie "/dev/sr0" or "scan".'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        os.umask(int('077', 8))

        if self._args.speed[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'CD/DVD device speed.'
            )
        if self._args.device[0] != 'scan' and not (
                os.path.exists(self._args.device[0])):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] +
                '" CD/DVD device.'
            )


class Cdrom:
    """
    CDROM class
    """

    def __init__(self) -> None:
        self._devices: dict = {}
        self.detect()

    def get_devices(self) -> dict:
        """
        Return list of devices
        """
        return self._devices

    def detect(self) -> None:
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
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
                        model += ' ' + ifile.readline().strip()
                except OSError:
                    continue
            self._devices[device] = model


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

    @staticmethod
    def config() -> None:
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
    def _cdspeed(device: str, speed: int) -> None:
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

    @staticmethod
    def _md5tao(device: str) -> None:
        isoinfo = command_mod.Command('isoinfo', errors='stop')

        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        tmpfile = os.path.join(tmpdir, 'md5cd.tmp' + str(os.getpid()))
        command = command_mod.Command('dd', errors='stop')
        command.set_args([
            'if=' + device,
            'bs=2048',
            'count=4096',
            'of=' + tmpfile
        ])
        task = subtask_mod.Batch(command.get_cmdline())
        task.run()
        if task.get_error('Permission denied$'):
            raise SystemExit(
                sys.argv[0] +
                ': Cannot read from CD/DVD device. Please check permissions.'
            )
        if not os.path.isfile(tmpfile):
            raise SystemExit(
                sys.argv[0] +
                ': Cannot find CD/DVD media. Please check drive.'
            )

        isoinfo.set_args(['-d', '-i', tmpfile])
        task2 = subtask_mod.Batch(isoinfo.get_cmdline())
        task2.run(pattern='^Volume size is: ')
        if not task2.has_output():
            raise SystemExit(
                sys.argv[0] +
                ': Cannot find TOC on CD/DVD media. Disk not recognised.'
            )
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task2.get_exitcode()) +
                ' received from "' + task2.get_file() + '".'
            )
        blocks = int(task2.get_output()[0].split()[-1])

        command.set_args(['if=' + device, 'bs=2048', 'count=' + str(blocks)])

        nice = command_mod.Command('nice', args=['-20'], errors='stop')
        child = subtask_mod.Child(
            nice.get_cmdline() + command.get_cmdline()).run()
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
        if 0 < pad < 16777216:
            md5.update(b'\0'*pad)  # Padding
        print(md5.hexdigest(), device, sep='  ')
        time.sleep(1)

        eject = command_mod.Command('eject', errors='ignore')
        if eject.is_found():
            task = subtask_mod.Batch(eject.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )

    @staticmethod
    def _scan() -> None:
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print("  {0:10s}  {1:s}".format(key, value))

    def run(self) -> int:
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

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
