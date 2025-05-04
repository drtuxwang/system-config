#!/usr/bin/env python3
"""
Resize large images to mega-pixels limit.
"""

import argparse
import math
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple

from command_mod import Command
from config_mod import Config
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

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def get_megs(self) -> float:
        """
        Return mega-pixels.
        """
        return self._args.megs[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Resize large images to mega-pixels limit.",
        )

        parser.add_argument(
            '-megs',
            nargs=1,
            type=float,
            default=[9],
            help="Select mega-pixels. Default is 9.",
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing JPEG files to resize.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = Command('convert', errors='stop')

        if self._args.megs[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                f'positive number for megabytes.',
            )

        for path in [Path(x) for x in self._args.directories]:
            if not path.is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Image directory '
                    f'"{path}" does not exist.',
                )


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

    def _imagesize(self, path: Path) -> Tuple[int, int]:
        self._convert.set_args(['-verbose', path, '/dev/null'])
        task = Batch(self._convert.get_cmdline())
        task.run(pattern='=>', error2output=True)
        if not task.has_output():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" image file.',
            )
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        x_size, y_size = task.get_output(
            )[0].split('=>')[1].split('+')[0].split()[-1].split('x')
        return int(x_size), int(y_size)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        self._convert = options.get_convert()
        megs = options.get_megs()
        images_extensions = Config().get('image_extensions')

        for directory in options.get_directories():
            for path in sorted(Path(directory).glob('*')):
                if path.suffix.lower() in images_extensions:
                    ix_size, iy_size = self._imagesize(path)
                    imegs = ix_size * iy_size / 1000000
                    print(
                        f"{path}: "
                        f"{ix_size} x "
                        f"{iy_size} "
                        f"({imegs:4.2f})",
                        end='',
                    )
                    resize = math.sqrt(megs / imegs)
                    ox_size = int(ix_size*resize + 0.5)
                    oy_size = int(iy_size*resize + 0.5)
                    if ox_size < ix_size and oy_size < iy_size:
                        print(
                            f" => {ox_size} x "
                            f"{oy_size} "
                            f"({ox_size * oy_size / 1000000:4.2f})",
                            end='',
                        )
                        self._convert.set_args([
                            '-verbose',
                            '-size',
                            f'{ox_size}x{oy_size}',
                            '-resize',
                            f'{ox_size}x{oy_size}!',
                            path,
                            path,
                        ])
                        task = Batch(self._convert.get_cmdline())
                        task.run()
                        if task.get_exitcode():
                            raise SystemExit(
                                f'{sys.argv[0]}: Error code '
                                f'{task.get_exitcode()} received from '
                                f'"{task.get_file()}".',
                            )
                    print()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
