#!/usr/bin/env python3
"""
Determine file information
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

import imagesize  # type: ignore
import magic  # type: ignore

from command_mod import Command
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
            description="Determine file information."
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
    def _get_info(cls, file: str) -> str:
        info = magic.from_file(file, mime=True)
        if info.startswith('image/'):
            x, y = imagesize.get(file)
            info = f'{info}  {x}:{y}'
        if info.startswith(('audio/', 'video/')):
            task = Batch(cls._ffprobe.get_cmdline() + [file])
            task.run(error2output=True)
            time = 0
            size = ''
            freq = ''
            for line in task.get_output():
                try:
                    if line.strip().startswith('Duration:'):
                        hrs, mins, secs = (
                            line.replace(',', '').split()[1].split(':')
                        )
                        time = int(int(hrs)*3600+int(mins)*60+float(secs))
                    elif line.strip().startswith('Stream #'):
                        if ' fps,' in line:
                            size = re.findall(
                                r'\d\d+x\d\d+',
                                line,
                            )[0].replace('x', ':')
                        elif ' Hz,' in line:
                            freq = f"{line.split(' Hz,')[0].split(', ')[-1]}"
                except (IndexError, ValueError):
                    pass
            if time:
                info = f'{info}  {time}s'
            if size:
                info = f'{info}  {size}'
            if freq:
                info = f'{info}  {freq}Hz'
        return info

    @classmethod
    def _show(cls, files: List[str]) -> None:
        files = [x for x in files if Path(x).is_file()]
        if files:
            width = max(Message(x).width() for x in files)
            for file in files:
                print(f"{Message(file).get(width)}  {cls._get_info(file)}")

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
