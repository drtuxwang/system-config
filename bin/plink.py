#!/usr/bin/env python3
"""
Create links to picture/video files.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import config_mod
import file_mod


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

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    f'{sys.argv[0]}: Source directory '
                    f'"{directory}" does not exist.',
                )
            if os.path.samefile(directory, os.getcwd()):
                raise SystemExit(
                    f'{sys.argv[0]}: Source directory '
                    f'"{directory}" cannot be current directory.',
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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        depth = options.get_depth()
        config = config_mod.Config()
        images_extensions = (
            config.get('image_extensions') + config.get('video_extensions')
        )

        for album, directory in enumerate(options.get_directories()):
            linkdir = '_'.join(directory.split(os.sep)[-depth:])
            for number, file in enumerate(
                sorted(glob.glob(os.path.join(directory, '*'))),
            ):
                ext = os.path.splitext(file)[1].lower()
                if ext in images_extensions:
                    link = f'{album+1:02d}.{number+1:02d}_{linkdir}{ext}'
                    if link.endswith(('.mp4', '.webm')):
                        link += '.gif'
                    if not os.path.islink(link):
                        try:
                            os.symlink(file, link)
                        except OSError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Cannot create "{link}" link.',
                            ) from exception
                        file_stat = file_mod.FileStat(file)
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
