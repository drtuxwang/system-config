#!/usr/bin/env python3
"""
Copy CD/DVD data as a portable ISO/BIN image file.
"""

import argparse
import glob
import logging
import os
import signal
import sys
import time
from typing import List

import command_mod
import logging_mod
import subtask_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_disk_at_once_flag(self) -> bool:
        """
        Return dao flag
        """
        return self._args.dao_flag

    def get_device(self) -> str:
        """
        Return device location.
        """
        return self._args.device[0]

    def get_image(self) -> str:
        """
        Return ISO/BIN image location.
        """
        return self._image

    def get_speed(self) -> str:
        """
        Return CD/DVD speed.
        """
        return self._args.speed[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Copy CD/DVD data as a portable ISO/BIN image file.',
        )

        parser.add_argument(
            '-dao',
            dest='dao_flag',
            action='store_true',
            help='Read data/audio/video CD in disk-at-once mode.'
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
        parser.add_argument(
            'image',
            nargs='?',
            metavar='image.iso|image.bin',
            help='ISO image file or BIN image filie for DAO mode.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.speed[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'CD/DVD device speed.'
            )
        if (
                self._args.device[0] != 'scan' and
                not os.path.exists(self._args.device[0])
        ):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] +
                '" CD/DVD device.'
            )

        if self._args.image:
            self._image = self._args.image[0]
        elif self._args.dao_flag:
            self._image = 'file.bin'
        else:
            self._image = 'file.iso'


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
    def _cdspeed(device: str, speed: str) -> None:
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
    def _dao(device: str, speed: str, file: str) -> None:
        cdrdao = command_mod.Command('cdrdao', errors='stop')

        cdrdao.set_args(['read-cd', '--device', device, '--read-raw'])
        if speed:
            cdrdao.extend_args(['--speed', speed])
        if file.endswith('.bin'):
            cdrdao.extend_args(['--datafile', file, file[:-4] + '.toc'])
        else:
            cdrdao.extend_args(['--datafile', file, file + '.toc'])

        nice = command_mod.Command('nice', args=['-20'], errors='stop')
        task = subtask_mod.Task(nice.get_cmdline() + cdrdao.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + cdrdao.get_file() + '".'
            )

    @staticmethod
    def _scan() -> None:
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print("  {0:10s}  {1:s}".format(key, value))

    def _tao(self, device: str, file: str) -> None:
        isoinfo = command_mod.Command('isoinfo', errors='stop')

        command = command_mod.Command('dd', errors='stop')
        command.set_args(
            ['if=' + device, 'bs=' + str(2048*4096), 'count=1', 'of=' + file])
        task = subtask_mod.Batch(command.get_cmdline())
        task.run()
        if task.get_error()[0].endswith('Permission denied'):
            raise SystemExit(
                sys.argv[0] + ': Cannot read from CD/DVD device. '
                'Please check permissions.'
            )
        if not os.path.isfile(file):
            raise SystemExit(
                sys.argv[0] +
                ': Cannot find CD/DVD media. Please check drive.'
            )
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )

        isoinfo.set_args(['-d', '-i', file])
        task = subtask_mod.Batch(isoinfo.get_cmdline())
        task.run(pattern='^Volume size is: ')
        if not task.has_output():
            raise SystemExit(
                sys.argv[0] + ': Cannot find TOC on CD/DVD media. '
                'Disk not recognised.'
            )
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        blocks = int(task.get_output()[0].split()[-1])

        task2 = subtask_mod.Task(isoinfo.get_cmdline())
        task2.run(pattern=' id: $')
        if task2.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task2.get_exitcode()) +
                ' received from "' + task2.get_file() + '".'
            )

        print('Creating ISO image file "' + file + '"...')
        command.set_args(
            ['if=' + device, 'bs=2048', 'count=' + str(blocks), 'of=' + file])

        nice = command_mod.Command('nice', args=['-20'], errors='stop')
        task2 = subtask_mod.Task(nice.get_cmdline() + command.get_cmdline())
        task2.run(pattern='Input/output error| records (in|out)$')

        if not os.path.isfile(file):
            raise SystemExit(
                sys.argv[0] + ': Cannot find CD/DVD media. '
                'Please check drive.'
            )
        pad = int(blocks * 2048 - os.path.getsize(file))
        if 0 < pad < 16777216:
            print(pad, 'bytes flushing from CD/DVD prefetch bug...')
            with open(file, 'ab') as ofile:
                ofile.write(b"\0" * pad)
        self._isosize(file, os.path.getsize(file))

    @staticmethod
    def _isosize(image: str, size: int) -> None:
        if size > 734003200:
            logger.info(
                "%s: %4.2f MB (%5.3f salesman's GB)",
                image,
                size/1048576,
                size/1000000000,
            )
            if size > 9400000000:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "9.4GB/240min Duel Layer DVD media."
                )
                logger.warning(
                    "==> Please split your data into "
                    "multiple images."
                )
            elif size > 4700000000:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "4.7GB/120min DVD media."
                )
                logger.warning(
                    "==> Please use Duel Layer DVD media or split "
                    "your data into multiple images."
                )
            else:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "700MB/80min CD media."
                )
                logger.warning(
                    "==> Please use DVD media or split your data "
                    "into multiple images."
                )
            print()
        else:
            minutes, remainder = divmod(size, 734003200 / 80)
            seconds = remainder * 4800 / 734003200.
            logger.info(
                "%s: %4.2f MB (%.0f min %05.2f sec)",
                image,
                size/1048576,
                minutes,
                seconds
            )
            if size > 681574400:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "650MB/74min CD media."
                )
                logger.warning("==> Please use 700MB/80min CD media instead.")

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        device = options.get_device()
        if device == 'scan':
            self._scan()
        else:
            speed = options.get_speed()
            file = options.get_image()

            self._cdspeed(device, speed)
            if os.path.isfile(file):
                try:
                    os.remove(file)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot over write "' + file +
                        '" CD/DVD image file.'
                    ) from exception
            if options.get_disk_at_once_flag():
                self._dao(device, speed, file)
            else:
                self._tao(device, file)
            time.sleep(1)
            eject = command_mod.Command('eject', errors='ignore')
            if eject.is_found():
                task = subtask_mod.Batch(eject.get_cmdline())
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
