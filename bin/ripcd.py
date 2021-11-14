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
from typing import List

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
        return self._args.device[0]

    def get_icedax(self) -> command_mod.Command:
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

        self._icedax = command_mod.Command('icedax', errors='stop')

        if self._args.speed[0] < 1:
            raise SystemExit(
                f"{sys.argv[0]}: You must specific a positive integer for "
                "CD/DVD device speed.",
            )
        if (
                self._args.device[0] != 'scan' and
                not os.path.exists(self._args.device[0])
        ):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._args.device[0]}" CD/DVD device.',
            )

        if self._args.tracks:
            self._tracks = self._args.tracks[0].split(',')
        else:
            self._tracks = []


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
            self._toc: list = []
            self._tracks: list = []
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

    def _rip_tracks(self, ntracks: int) -> None:
        tee = command_mod.Command('tee', errors='stop')

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
            logfile = track.zfill(2) + '.log'
            try:
                with open(
                    logfile,
                    'w',
                    encoding='utf-8',
                    newline='\n',
                ) as ofile:
                    line = (
                        f'\nRipping track {track}/{ntracks} ({length} seconds)'
                    )
                    print(line)
                    print(line, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{logfile}" file.',
                ) from exception
            warnfile = track.zfill(2) + '.warning'
            try:
                with open(warnfile, 'wb'):
                    pass
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{warnfile}" file.',
                ) from exception
            wavfile = track.zfill(2) + '.wav'
            tee.set_args(['-a', logfile])
            task = subtask_mod.Task(self._icedax.get_cmdline() + [
                'verbose-level=disable',
                f'track={track}',
                f'dev={self._device}',
                wavfile,
                '2>&1',
                '|'
                ] + tee.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            if os.path.isfile(wavfile):
                self._pregap(wavfile)
            if not self._hasprob(logfile):
                os.remove(warnfile)

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
            with open(
                '00.log',
                'w',
                encoding='utf-8',
                newline='\n',
            ) as ofile:
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
    def _hasprob(logfile: str) -> bool:
        with open(logfile, encoding='utf-8', errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip('\r\n')
                if line.endswith('problems'):
                    if line[-14:] != 'minor problems':
                        ifile.close()
                        return True
        return False

    @staticmethod
    def _pregap(wavfile: str) -> None:
        # 1s = 176400 bytes
        size = os.path.getsize(wavfile)
        with open(wavfile, 'rb+') as ifile:
            ifile.seek(size - 2097152)
            data = ifile.read(2097152)
            for i in range(len(data) - 1, 0, -1):
                if data[i] != 0:
                    newsize = size - len(data) + i + 264
                    if newsize < size:
                        line = (
                            f'Track length is {str(newsize)} '
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
        task = subtask_mod.Batch(self._icedax.get_cmdline())
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
