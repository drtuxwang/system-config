#!/usr/bin/env python3
"""
Create links to picture/video files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from config_mod import Config
from file_mod import FileStat


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_depth(self) -> int:
        """
        Return directory depth
        """
        return self._args.depth[0]

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Create links to picture/video files.",
        )

        parser.add_argument(
            '-depth',
            nargs=1,
            type=int,
            default=[1],
            help="Number of directories to ad to link name.",
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing JPEG files to link.",
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
                    f'{sys.argv[0]}: Source directory '
                    f'"{path}" does not exist.',
                )
            if path.samefile(Path.cwd()):
                raise SystemExit(
                    f'{sys.argv[0]}: Source directory '
                    f'"{path}" cannot be current directory.',
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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        depth = options.get_depth()
        config = Config()
        images_extensions = (
            config.get('image_extensions') + config.get('video_extensions')
        )

        for album, directory in enumerate(options.get_directories()):
            linkdir = '_'.join(directory.split(os.sep)[-depth:])
            for number, file in enumerate(sorted([
                x
                for x in Path(directory).glob('*.*')
                if x.suffix.lower() in images_extensions
            ])):
                ext = Path(file).suffix.lower()
                if ext in images_extensions:
                    link = Path(f'{album+1:02d}.{number+1:03d}_{linkdir}{ext}')
                    if not link.is_symlink():
                        try:
                            link.symlink_to(file)
                        except OSError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Cannot create "{link}" link.',
                            ) from exception
                        file_stat = FileStat(file)
                        file_time = file_stat.get_time()
                        try:
                            os.utime(
                                link,
                                (file_time, file_time),
                                follow_symlinks=False,
                            )
                        except NotImplementedError:
                            pass

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
