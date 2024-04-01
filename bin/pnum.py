#!/usr/bin/env python3
"""
Renumber picture/video files into a numerical series.
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

from config_mod import Config


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directories(self) -> List[Path]:
        """
        Return list of directories.
        """
        return [Path(x) for x in self._args.directories]

    def get_order(self) -> str:
        """
        Return order method.
        """
        return self._args.order

    def get_reset_flag(self) -> bool:
        """
        Return per directory number reset flag
        """
        return self._args.reset_flag

    def get_start(self) -> int:
        """
        Return start number.
        """
        return self._args.start[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Renumber picture files into a numerical series.",
        )

        parser.add_argument(
            '-time',
            action='store_const',
            const='time',
            dest='order',
            default='file',
            help="Sort using modification time.",
        )
        parser.add_argument(
            '-noreset',
            dest='reset_flag',
            action='store_false',
            help="Use same number sequence for all directories.",
        )
        parser.add_argument(
            '-start',
            nargs=1,
            type=int,
            default=[1],
            help="Select number to start from.",
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing picture/video files.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        for path in [Path(x) for x in self._args.directories]:
            if not path.is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Picture directory '
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

    @staticmethod
    def _sorted(options: Options, paths: List[Path]) -> List[Path]:
        order = options.get_order()
        if order == 'time':
            return sorted(paths, key=lambda x: (x.stat().st_mtime, x))
        return sorted(paths)

    @staticmethod
    def _rename(number: int, paths: List[Path]) -> None:
        paths_new = []

        for path in paths:
            extension = path.suffix.lower().replace('.jpeg', '.jpg')
            path_new = Path(f'pic{number:05d}{extension}')
            paths_new.append(path_new)
            try:
                path.replace(f'pnum.tmp-{path_new}')
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot rename "{path}" image file.',
                ) from exception
            number += 1

        for path in paths_new:
            try:
                Path(f'pnum.tmp-{path}').replace(path)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot rename to '
                    f'"{path}" image file.',
                ) from exception

    @staticmethod
    def _set_time(path: Path) -> None:
        dir_time = path.stat().st_mtime
        file_times = [x.stat().st_mtime for x in path.glob('*') if x.is_file()]
        if file_times:
            mtime = max(file_times)
            if mtime != dir_time:
                os.utime(path, (mtime, mtime))

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        startdir = os.getcwd()
        reset_flag = options.get_reset_flag()
        number = options.get_start()
        config = Config()
        images_extensions = (
            config.get('image_extensions') + config.get('video_extensions')
        )

        isvalid = re.compile(r'pic\d{5}\.')
        for path in [x for x in options.get_directories() if x.is_dir()]:
            os.chdir(path)
            paths = sorted([
                x
                for x in Path().glob('*.*')
                if x.suffix.lower() in images_extensions
            ])
            paths_valid = [x for x in paths if isvalid.match(x.name)]
            paths_sorted = self._sorted(options, paths)
            if paths != paths_valid or paths != paths_sorted:
                print(f"Renaming image files: {path}")
                if reset_flag:
                    number = options.get_start()
                self._rename(number, paths_sorted)
                self._set_time(Path())
            os.chdir(startdir)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
