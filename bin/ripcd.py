#!/usr/bin/env python3
"""
Rip CD audio tracks as WAVE sound files.
"""

import argparse
import glob
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

from subtask_mod import Batch, Task
from command_mod import Command


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

    def get_icedax(self) -> Command:
        """
        Return icedax Command class object.
        """
        return self._icedax

    def get_speed(self) -> int:
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def get_tracks(self) -> List[str]:
        """
        Return list of track numbers.
        """
        return self._tracks

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Rip CD audio tracks as WAVE sound files.",
        )

        parser.add_argument(
            '-speed',
            nargs=1,
            type=int,
            default=[8],
            help="Select CD spin speed.",
        )
        parser.add_argument(
            '-tracks',
            nargs=1,
            metavar='n[,n...]',
            help="Select CD tracks to rip.",
        )
        parser.add_argument(
            'device',
            nargs=1,
            metavar='device|scan',
            help='CD/DVD device (ie "/dev/sr0" or "scan".',
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._icedax = Command('icedax', errors='stop')

        if self._args.speed[0] < 1:
            raise SystemExit(
                f"{sys.argv[0]}: You must specific a positive integer for "
                "CD/DVD device speed.",
            )
        if (
            self._args.device[0] != 'scan' and
            not Path(self._args.device[0]).exists()
        ):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._args.device[0]}" CD/DVD device.',
            )

        self._tracks = (
            self._args.tracks[0].split(',') if self._args.tracks else []
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
            self._toc: list = []
            self._tracks: list = []
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

    def _rip_tracks(self, ntracks: int) -> None:
        tee = Command('tee', errors='stop')

        for track in self._tracks:
            istrack = re.compile(f'^.* {track}[.]\\( *')
            length = 'Unknown'
            for line in self._toc:
                if istrack.search(line):
                    minutes, seconds = istrack.sub(
                        '',
                        line
                    ).split(')')[0].split(':')
                    try:
                        length = f'{int(minutes)*60 + float(seconds):4.2f}'
                    except ValueError:
                        pass
                    break

            log_path = Path(f'{track.zfill(2)}.log')
            try:
                with log_path.open('w') as ofile:
                    line = (
                        f'\nRipping track {track}/{ntracks} ({length} seconds)'
                    )
                    print(line)
                    print(line, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{log_path}" file.',
                ) from exception

            warn_path = Path(f'{track.zfill(2)}.warning')
            try:
                warn_path.touch()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{warn_path}" file.',
                ) from exception

            wav_path = Path(f'{track.zfill(2)}.wav')
            tee.set_args(['-a', log_path])
            task = Task(self._icedax.get_cmdline() + [
                'verbose-level=disable',
                f'track={track}',
                f'dev={self._device}',
                wav_path,
                '2>&1',
                '|'
                ] + tee.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            if wav_path.is_file():
                self._pregap(wav_path)
            if not self._hasprob(log_path):
                os.remove(warn_path)

    def _rip(self) -> None:
        self._icedax.set_args([
            '-vtrackid',
            '-paranoia',
            f'-S={self._speed}',
            '-K',
            'dsp',
            '-H'
        ])
        try:
            with Path('00.log').open('w') as ofile:
                for line in self._toc:
                    print(line, file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "00.log" TOC file.',
            ) from exception
        try:
            ntracks = int(self._toc[-1].split('.(')[-2].split()[-1])
        except (IndexError, ValueError) as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Unable to detect the number of audio tracks.",
            ) from exception
        if not self._tracks:
            self._tracks = [str(i) for i in range(1, int(ntracks) + 1)]

        self._rip_tracks(ntracks)

    @staticmethod
    def _hasprob(log_path: Path) -> bool:
        with log_path.open(errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip('\n')
                if line.endswith('problems'):
                    if line[-14:] != 'minor problems':
                        ifile.close()
                        return True
        return False

    @staticmethod
    def _pregap(wav_path: Path) -> None:
        # 1s = 176400 bytes
        size = wav_path.stat().st_size
        with wav_path.open('rb+') as ifile:
            ifile.seek(size - 2097152)
            data = ifile.read(2097152)
            for i in range(len(data) - 1, 0, -1):
                if data[i] != 0:
                    newsize = size - len(data) + i + 264
                    if newsize < size:
                        line = (
                            f'Track length is {newsize} '
                            f'bytes (pregap removed)',
                        )
                        print(line)
                        ifile.truncate(newsize)
                    break

    @staticmethod
    def _scan() -> None:
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print(f"  {key:10s}  {value}")

    def _read_toc(self) -> None:
        self._icedax.set_args([
            '-info-only',
            '--no-infofile',
            'verbose-level=toc',
            f'dev={self._device}',
            f'speed={self._speed}',
        ])
        task = Batch(self._icedax.get_cmdline())
        task.run()
        self._toc = task.get_error(r'[.]\(.*:.*\)')
        if not self._toc:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find Audio CD media. '
                'Please check drive.',
            )
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        for line in task.get_error(r'[.]\(.*:.*\)|^CD'):
            print(line)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._icedax = options.get_icedax()
        self._device = options.get_device()
        self._speed = options.get_speed()
        self._tracks = options.get_tracks()

        if self._device == 'scan':
            self._scan()
        else:
            self._read_toc()
            self._rip()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
