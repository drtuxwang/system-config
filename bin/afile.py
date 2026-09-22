#!/usr/bin/env python3
"""
Determine audio file information
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from config_mod import Mime
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
            description="Determine audio file information."
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
    def _get_ffprobe(cls, file: str) -> str:
        task = Batch(cls._ffprobe.get_cmdline() + [file])
        task.run(error2output=True)
        info = ''
        time = 0
        freq = ''
        for line in task.get_output():
            try:
                if line.strip().startswith('Duration:'):
                    hrs, mins, secs = (
                        line.replace(',', '').split()[1].split(':')
                    )
                    time = int(int(hrs)*3600+int(mins)*60+float(secs))
                elif line.strip().startswith('Stream #'):
                    if ' Hz,' in line:
                        freq = f"{line.split(' Hz,')[0].split(', ')[-1]}"
            except (IndexError, ValueError):
                pass
        if time:
            info = f'{info}  {time}s'
        if freq:
            info = f'{info}  {freq}Hz'
            return info
        return ''

    @classmethod
    def _show(cls, files: List[str]) -> None:
        files = [x for x in files if Path(x).is_file()]
        if files:
            width = max(Message(x).width() for x in files)
            for file in files:
                info = Mime.get(Path(file))
                if info.startswith(('audio/', 'video/')):
                    info = f'{info}{cls._get_ffprobe(file)}'
                    if '  ' in info:
                        print(f"{Message(file).get(width)}  {info}")

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
