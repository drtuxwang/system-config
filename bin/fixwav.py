#!/usr/bin/env python3
"""
Normalize volume of wave files (-16.0dB rms mean volume).
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def get_ffmpeg(self) -> command_mod.Command:
        """
        Return ffmpeg Command class object.
        """
        return self._ffmpeg

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Normalize volume of wave files "
            "(-16.0dB rms mean volume).",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="View volume only.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.wav',
            help="Audio file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._ffmpeg = command_mod.Command('ffmpeg', errors='stop')


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

    def _adjust(self, path: Path, volume: str) -> None:
        change = -16 - float(volume)
        path_new = Path(f'{path}.part')

        self._ffmpeg.set_args([
            '-i',
            path,
            '-af',
            f'volume={change}dB',
            '-y',
            '-f',
            'wav',
            path_new
        ])
        task = subtask_mod.Batch(self._ffmpeg.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
            )
        try:
            path_new.replace(path)
        except OSError as exception:
            path_new.unlink()
            raise SystemExit(
                f'{sys.argv[0]}: Cannot update "{path}" file.',
            ) from exception

    def _view(self, path: Path) -> Tuple[str, str]:
        self._ffmpeg.set_args(
            ['-i', path, "-af", "volumedetect", "-f", "null", "/dev/null"]
        )
        task = subtask_mod.Batch(self._ffmpeg.get_cmdline())
        task.run(pattern=' (mean|max)_volume: .* dB$', error2output=True)
        if len(task.get_output()) != 2:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read corrupt "{path}" wave file.',
            )
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
            )
        volume = task.get_output()[0].split()[-2]
        pvolume = task.get_output()[1].split()[-2]
        return volume, pvolume

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._ffmpeg = options.get_ffmpeg()

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')
            if path.suffix != '.wav':
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot handle "{path}" non-wave file.',
                )
            volume, pvolume = self._view(path)
            sys.stdout.write(f"{path}: {volume} dB ({pvolume} dB peak)")
            if not options.get_view_flag():
                for npass in range(4):
                    self._adjust(path, volume)
                    sys.stdout.write(f" {npass}>> ")
                    volume, pvolume = self._view(path)
                    sys.stdout.write(f"{volume} dB ({pvolume} dB peak)")
                    if volume.startswith('-16.'):
                        break
            print()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
