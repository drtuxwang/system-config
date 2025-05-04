#!/usr/bin/env python3
"""
Determine video file information
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

import magic  # type: ignore

from command_mod import Command
from config_mod import Config
from logging_mod import Message
from subtask_mod import Batch


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
        parser = argparse.ArgumentParser(
            description="Determine video file information."
        )

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
    _ffprobe = Command('ffprobe', errors='stop')
    _isjunk1 = re.compile(r'( \[SAR[^,]*)?, (\d* kb/s|\d+.\d+ fps),.*')
    _isjunk2 = re.compile(r'ISO Media, | .*')
    _video_extensions = Config().get('video_extensions')

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
    def _get_media_info(cls, path: Path, info: str) -> str:
        task = Batch(cls._ffprobe.get_cmdline() + [path])
        task.run(error2output=True)
        video_type = cls._isjunk2.sub('', info)
        video_time = 0
        video_size = '?:?'
        video_freq = '?Hz'
        for line in task.get_output():
            try:
                if line.strip().startswith('Duration:'):
                    hrs, mins, secs = (
                        line.replace(',', '').split()[1].split(':')
                    )
                    video_time = int(int(hrs)*3600+int(mins)*60+float(secs))
                elif line.strip().startswith('Stream #'):
                    if ' fps,' in line:
                        size = cls._isjunk1.sub('', line).split(', ')[-1]
                        video_size = size.replace('x', ':')
                    elif ' Hz,' in line:
                        video_freq = f"{line.split(' Hz,')[0].split(', ')[-1]}"
            except IndexError:
                pass
        return f'{video_type} {video_time}s {video_size} {video_freq}Hz'

    @classmethod
    def _show(cls, files: List[str]) -> None:
        width = max(Message(x).width() for x in files)
        with magic.Magic() as checker:
            for file in files:
                path = Path(file)
                if path.suffix in cls._video_extensions:
                    info = checker.id_filename(file)
                    print(
                        f"{Message(file).get(width)}  "
                        f"{cls._get_media_info(path, info)}"
                    )

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        files = options.get_files()

        cls._show(files)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
