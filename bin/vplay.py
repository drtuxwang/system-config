#!/usr/bin/env python3
"""
Play AVI/FLV/MP4 files in directory.
"""

import argparse
import os
import random
import signal
import sys
from pathlib import Path
from typing import Any, List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def get_shuffle_flag(self) -> bool:
        """
        Return shuffle flag.
        """
        return self._args.shuffle_flag

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Play AVI/FLV/MP4 video files in directory.",
        )

        parser.add_argument(
            '-s',
            dest='shuffle_flag',
            action='store_true',
            help="Shuffle order of the media files.",
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="View information.",
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Video directory.",
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
    def _get_files(directory: str, *patterns: Any) -> List[str]:
        files: list = []
        for pattern in patterns:
            files.extend(Path(directory).glob(pattern))
        return sorted([str(x) for x in files])

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        play = Command('play', errors='stop')
        if options.get_view_flag():
            play.set_args(['-v'])
        for directory in options.get_directories():
            if not Path(directory).is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find '
                    f'"{directory}" media directory.',
                )
            files = self._get_files(directory, '*.avi', '*.flv', '*.mp4')
            if options.get_shuffle_flag():
                random.shuffle(files)
            play.extend_args(files)

        task = Task(play.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
