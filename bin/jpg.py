#!/usr/bin/env python3
"""
Convert images to JPEG files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from config_mod import Config
from file_mod import FileStat
from subtask_mod import Batch


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_convert(self) -> Command:
        """
        Return convert Command class object.
        """
        return self._convert

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Convert images to JPEG files.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Image file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = Command('convert', errors='stop')


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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        convert = options.get_convert()
        images_extensions = [
            x
            for x in Config().get('image_extensions')
            if x != '.jpg'
        ]

        for file in options.get_files():
            path = Path(file)
            if path.is_file() and path.suffix.lower() in images_extensions:
                path_new = path.with_suffix('.jpg')
                if not path_new.exists():
                    print(f"{path} => {path_new}")
                    task = Batch(convert.get_cmdline() + [path, path_new])
                    task.run()
                    if task.get_exitcode():
                        raise SystemExit(
                            f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                            f'received from "{task.get_file()}".',
                        )
                    file_time = FileStat(path).get_mtime()
                    os.utime(path_new, (file_time, file_time))
        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
