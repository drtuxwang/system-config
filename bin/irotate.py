#!/usr/bin/env python3
"""
Rotate image file clockwise.
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

    def get_rotation(self) -> int:
        """
        Return rotation in degrees.
        """
        return self._args.rotation[0]

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Rotate image file clockwise.",
        )

        parser.add_argument(
            '-r',
            nargs=1,
            type=int,
            dest='rotation',
            default=[90],
            metavar='deg',
            help="Rotation in degrees.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Image file to rotate.',
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
            self._tempfiles: List[str] = []
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

        convert = Command('convert', errors='stop')
        convert.set_args(['-rotate', options.get_rotation()])

        images_extensions = Config().get('image_extensions')
        for path in [Path(x) for x in options.get_files()]:
            if path.is_file() and path.suffix.lower() in images_extensions:
                path_tmp = Path(f'{path}-rotate{path.suffix}')
                task = Batch(convert.get_cmdline() + [path, path_tmp])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
                file_time = FileStat(path).get_mtime()
                os.utime(path_tmp, (file_time, file_time))
                path_tmp.replace(path)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
