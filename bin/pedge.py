#!/usr/bin/env python3
"""
Add border to image edges.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

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

    def get_flags(self) -> List[str]:
        """
        Return convert operations flags.
        """
        default = not any((
            self._args.north_flag,
            self._args.east_flag,
            self._args.south_flag,
            self._args.west_flag,
        ))
        pixels = self.get_pixels()

        flags = ['-background', f'#{self.get_rgb()}']
        if self._args.north_flag or default:
            flags.extend(['-gravity', 'north', '-splice', f'0x{pixels}'])
        if self._args.east_flag or default:
            flags.extend(['-gravity', 'east', '-splice', f'{pixels}x0'])
        if self._args.south_flag or default:
            flags.extend(['-gravity', 'south', '-splice', f'0x{pixels}'])
        if self._args.west_flag or default:
            flags.extend(['-gravity', 'west', '-splice', f'{pixels}x0'])

        return flags

    def get_pixels(self) -> int:
        """
        Return border pixels.
        """
        return self._args.pixels[0]

    def get_rgb(self) -> str:
        """
        Return rgb colour.
        """
        return self._args.rgb[0]

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Add border to image edges.",
        )

        parser.add_argument(
            '-n',
            dest='north_flag',
            action='store_true',
            help="Add border to north (top) edge.",
        )
        parser.add_argument(
            '-e',
            dest='east_flag',
            action='store_true',
            help="Add border to east (right) edge.",
        )
        parser.add_argument(
            '-s',
            dest='south_flag',
            action='store_true',
            help="Add border to south (bottom) edge.",
        )
        parser.add_argument(
            '-w',
            dest='west_flag',
            action='store_true',
            help="Add border to west (left) edge.",
        )
        parser.add_argument(
            '-p',
            nargs=1,
            type=int,
            dest='pixels',
            default=[100],
            help="Select pixel size. Default is 100.",
        )
        parser.add_argument(
            '-rgb',
            nargs=1,
            default='ffffff',
            help="Select rgb colour. Default is ffffff.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Image file to add border.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = Command('convert', errors='stop')

        if self._args.pixels[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                f'positive number for pixels.',
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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        cmdline = options.get_convert().get_cmdline() + options.get_flags()

        images_extensions = Config().get('image_extensions')
        for path in [Path(x) for x in options.get_files()]:
            if path.is_file() and path.suffix.lower() in images_extensions:
                task = Batch(cmdline + [path, path])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code '
                        f'{task.get_exitcode()} received from '
                        f'"{task.get_file()}".',
                    )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
