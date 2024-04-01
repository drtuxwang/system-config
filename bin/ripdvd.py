#!/usr/bin/env python3
"""
Rip Video DVD title to file.
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch, Task


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

    def get_vlc(self) -> Command:
        """
        Return vlc Command class object.
        """
        return self._vlc

    def get_speed(self) -> int:
        """
        Return DVD speed.
        """
        return self._args.speed[0]

    def get_title(self) -> str:
        """
        Return DVD title.
        """
        return self._args.title[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Rip Video DVD title to file.",
        )

        parser.add_argument(
            '-speed',
            nargs=1,
            type=int,
            default=[8],
            help="Select DVD spin speed.",
        )
        parser.add_argument(
            '-title',
            nargs=1,
            type=int,
            default=[1],
            help="Select DVD title to rip (Default is 1).",
        )
        parser.add_argument(
            'device',
            nargs=1,
            metavar='device|scan',
            help='DVD device (ie "/dev/sr0" or "scan".',
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._vlc = Command('vlc', errors='stop')

        if self._args.speed[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for DVD device speed.',
            )
        if self._args.title[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for DVD title.',
            )
        if (
            self._args.device[0] != 'scan' and
            not Path(self._args.device[0]).exists()
        ):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._args.device[0]}" DVD device.',
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
            device = f'/dev/{Path(directory).parent.name}'
            model = ''
            for path in [Path(directory, x) for x in ('vendor', 'model')]:
                try:
                    with path.open(errors='replace') as ifile:
                        model += f' {ifile.readline().strip()}'
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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _cdspeed(device: str, speed: int) -> None:
        cdspeed = Command('cdspeed', errors='ignore')
        if cdspeed.is_found():
            if speed:
                cdspeed.set_args([device, speed])
            # If CD/DVD spin speed change fails its okay
            Task(cdspeed.get_cmdline()).run()
        elif speed and Path('/sbin/hdparm').is_file():
            hdparm = Command('/sbin/hdparm', errors='ignore')
            hdparm.set_args(['-E', speed, device])
            Batch(hdparm.get_cmdline()).run()

    def _rip(self) -> None:
        file = f'title-{str(self._title).zfill(2)}.mpg'
        self._vlc.set_args([
            f'dvdsimple:/{self._device}:#{self._title}',
            '--sout',
            f'#standard{{access=file,mux=ts,dst={file}}}',
            '--no-repeat',
            '--no-loop',
            '--play-and-exit',
        ])
        Task(self._vlc.get_cmdline()).run()

    @staticmethod
    def _scan() -> None:
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print(f"  {key:10s}  {value}")

    def run(self) -> int:
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

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
