#!/usr/bin/env python3
"""
Determine file type
"""

import argparse
import os
import re
import signal
import sys
import unicodedata
from pathlib import Path
from typing import List

import magic  # type: ignore

import command_mod
import config_mod
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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="determine file type.")

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to view.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """
    _ffprobe = command_mod.Command('ffprobe', errors='ignore')
    _isjunk = re.compile(r'( \[SAR[^,]*)?, (\d* kb/s|\d+.\d+ fps),.*')
    _video_extensions = config_mod.Config().get('video_extensions')

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

    @classmethod
    def _show(cls, pad: int, path: Path, info: str) -> None:
        if path.suffix in cls._video_extensions and cls._ffprobe.is_found():
            task = subtask_mod.Batch(cls._ffprobe.get_cmdline() + [path])
            task.run(error2output=True)
            length = 0
            size = '?x?'
            freq = '?Hz'
            for line in task.get_output():
                try:
                    if line.strip().startswith('Duration:'):
                        hrs, mins, secs = (
                            line.replace(',', '').split()[1].split(':')
                        )
                        length = int(int(hrs)*3600+int(mins)*60+float(secs))
                    elif line.strip().startswith('Stream #'):
                        if ' fps,' in line:
                            size = cls._isjunk.sub('', line).split(', ')[-1]
                        elif ' Hz,' in line:
                            freq = f"{line.split(' Hz,')[0].split(', ')[-1]}"
                except IndexError:
                    pass
            info = f'{length}s, {size}, {freq}Hz, {info}'

        print(f"{path}:{' '*pad} {info}")

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        files = options.get_files()

        cjk_widths = {
            x: sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in x)
            for x in files
        }
        max_len = max(cjk_widths.values())
        with magic.Magic() as checker:
            for file in files:
                pad = max_len - cjk_widths[file]
                cls._show(pad, Path(file), checker.id_filename(file))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
