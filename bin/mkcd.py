#!/usr/bin/env python3
"""
Make data/audio/video CD/DVD using CD/DVD writer.
"""

import argparse
import glob
import os
import signal
import sys
import time
import types
from typing import Any, Callable, List, Union

import command_mod
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
        return self._device

    def get_erase_flag(self) -> bool:
        """
        Return erase flag.
        """
        return self._args.erase_flag

    def get_image(self) -> str:
        """
        Return ISO/BIN image file or audio directory.
        """
        return self._args.image[0]

    def get_speed(self) -> int:
        """
        Return CD speed.
        """
        return self._args.speed[0]

    @staticmethod
    def _detect_device(device: str) -> str:
        if not device:
            cdrom = Cdrom()
            if not cdrom.get_devices().keys():
                raise SystemExit(
                    f"{sys.argv[0]}: Cannot find any CD/DVD device.",
                )
            device = sorted(cdrom.get_devices())[0]
        if not os.path.exists(device):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{device}" CD/DVD device.',
            )
        return device

    @staticmethod
    def _signal_ignore(
        # pylint: disable=no-member
        _signal: int,
        _frame: types.FrameType,
    ) -> Union[
        Callable[[signal.Signals, types.FrameType], Any],
        int,
        signal.Handlers,
        None,
    ]:
        pass

    def _signal_trap(self) -> None:
        signal.signal(signal.SIGINT, self._signal_ignore)
        signal.signal(signal.SIGTERM, self._signal_ignore)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make data/audio/video CD/DVD using CD/DVD writer.",
        )

        parser.add_argument(
            '-dev',
            nargs=1,
            dest='device',
            help="Select device (ie /dev/sr0).",
        )
        parser.add_argument(
            '-erase',
            dest='erase_flag',
            action='store_true',
            help="Erase TOC on CD-RW media before writing in DAO mode.",
        )
        parser.add_argument(
            '-speed',
            nargs=1,
            type=int,
            default=[8],
            help="Select CD/DVD spin speed.",
        )
        parser.add_argument(
            'image',
            nargs=1,
            metavar='image.iso|image.bin|directory|scan',
            help="ISO/Bin image file, audio or scan",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.image != 'scan':
            self._device = self._detect_device(self._args.device)
        self._signal_trap()

        if self._args.speed[0] < 1:
            raise SystemExit(
                f"{sys.argv[0]}: You must specific a positive integer for "
                "CD/DVD device speed.",
            )
        if (
            self._args.image[0] != 'scan' and
            not os.path.isdir(self._args.image[0])
        ):
            if not os.path.exists(self._args.image[0]):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find '
                    f'"{self._args.image[0]}" CD/DVD device.',
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
            device = f'/dev/{os.path.basename(os.path.dirname(directory))}'
            model = ''
            for file in ('vendor', 'model'):
                try:
                    with open(
                        os.path.join(directory, file),
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
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
    def _eject() -> None:
        eject = command_mod.Command('eject', errors='ignore')
        if eject.is_found():
            time.sleep(1)
            task = subtask_mod.Batch(eject.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    @staticmethod
    def _scan() -> None:
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print(f"  {key:10s}  {value}")

    def _disk_at_once_data(self, options: Options) -> None:
        cdrdao = command_mod.Command('cdrdao', errors='stop')
        if options.get_erase_flag():
            cdrdao.set_args([
                'blank',
                '--blank-mode',
                'minimal',
                '--device',
                self._device,
                '--speed',
                str(self._speed)
            ])
            task = subtask_mod.Task(cdrdao.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
        cdrdao.set_args(
            ['write', '--device', self._device, '--speed', str(self._speed)])
        if os.path.isfile(self._image[:-4]+'.toc'):
            cdrdao.extend_args([self._image[:-4]+'.toc'])
        else:
            cdrdao.extend_args([self._image[:-4]+'.cue'])
        task = subtask_mod.Task(cdrdao.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        self._eject()

    def _track_at_once_audio(self) -> None:
        files = sorted(glob.glob(os.path.join(self._image, '*.wav')))

        wodim = command_mod.Command('wodim', errors='stop')
        print(
            "If your media is a rewrite-able CD/DVD its contents "
            "will be deleted."
        )
        answer = input(
            "Do you really want to burn data to this CD/DVD disk? (y/n) [n] ")
        if answer.lower() != 'y':
            raise SystemExit(1)
        print("Using AUDIO mode for WAVE files (Audio tracks detected)...")
        wodim.set_args([
            '-v',
            '-shorttrack',
            '-audio',
            '-pad',
            '-copy',
            f'dev={self._device}',
            f'speed={self._speed}',
            'driveropts=burnfree'
        ] + files)
        task = subtask_mod.Task(wodim.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

        time.sleep(1)
        icedax = command_mod.Command('icedax', errors='ignore')
        if icedax.is_found():
            icedax.set_args([
                '-info-only',
                '--no-infofile',
                'verbose-level=toc',
                f'dev={self._device}',
                f'speed={self._speed}',
            ])
            task2 = subtask_mod.Batch(icedax.get_cmdline())
            task2.run()
            toc = task2.get_error(r'[.]\(.*:.*\)|^CD')
            if not toc:
                raise SystemExit(
                    f"{sys.argv[0]}: Cannot find Audio CD media. "
                    "Please check drive.",
                )
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task2.get_exitcode()} '
                    f'received from "{task2.get_file()}".',
                )
            for line in toc:
                print(line)
        self._eject()

    def _track_at_once_data(self, options: Options) -> None:
        file = options.get_image()

        wodim = command_mod.Command('wodim', errors='stop')
        print(
            'If your media is a rewrite-able CD/DVD its contents will '
            'be deleted.'
        )
        answer = input(
            "Do you really want to burn data to this CD/DVD disk? (y/n) [n] "
        )
        if answer.lower() != 'y':
            raise SystemExit(1)
        wodim.set_args(['-v', '-shorttrack', '-eject'])

        # Pad to avoid dd read problem
        if os.path.getsize(file) < 2097152:
            wodim.append_arg('-pad')
        wodim.set_args([
            f'dev={self._device}',
            f'speed={self._speed}',
            'driveropts=burnfree',
            file,
        ])
        task = subtask_mod.Task(wodim.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._device = options.get_device()
        self._speed = options.get_speed()
        self._image = options.get_image()

        if self._image == 'scan':
            self._scan()
        elif os.path.isdir(self._image):
            self._track_at_once_audio()
        elif self._image.endswith('.bin'):
            self._disk_at_once_data(options)
        else:
            self._track_at_once_data(options)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
