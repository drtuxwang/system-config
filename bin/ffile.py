#!/usr/bin/env python3
"""
Determine file type
"""

import argparse
import re
import signal
import sys
from typing import List

import magic  # type: ignore

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
        return self._args.files

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
    _isjunk = re.compile(r'( \[SAR[^,]*)?, \d* kb/s,.*')

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
    def _show(cls, file: str, info: str) -> None:
        if 'MP4' in info and cls._ffprobe.is_found():
            task = subtask_mod.Batch(cls._ffprobe.get_cmdline() + [file])
            task.run(error2output=True)
            for line in task.get_output():
                try:
                    if line.strip().startswith('Duration:'):
                        duration = line.replace(',', '').split()[1]
                        info += f', {duration}'
                    elif line.strip().startswith('Stream #'):
                        if ' Hz,' in line:
                            freq = line.split(' Hz,')[0].split(', ')[-1]
                            info += f', {freq} Hz'
                        elif ' kb/s,' in line:
                            size = cls._isjunk.sub('', line).split(', ')[-1]
                            info += f', {size}'
                except IndexError:
                    pass

        print(f"{file}: {info}")

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        with magic.Magic() as checker:
            for file in options.get_files():
                cls._show(file, checker.id_filename(file))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
