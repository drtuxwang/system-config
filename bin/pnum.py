#!/usr/bin/env python3
"""
Renumber picture/video files into a numerical series.
"""

import argparse
import glob
import os
import shutil
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

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

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

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    f'{sys.argv[0]}: Picture directory '
                    f'"{directory}" does not exist.',
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
    def _sorted(
        options: Options,
        file_stats: List[file_mod.FileStat],
    ) -> List[file_mod.FileStat]:
        order = options.get_order()
        if order == 'time':
            file_stats = sorted(
                file_stats,
                key=lambda s: (s.get_time(), s.get_file())
            )
        else:
            file_stats = sorted(file_stats, key=lambda s: s.get_file())
        return file_stats

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        startdir = os.getcwd()
        reset_flag = options.get_reset_flag()
        number = options.get_start()
        config = config_mod.Config()
        images_extensions = (
            config.get('image_extensions') + config.get('video_extensions')
        )

        for directory in options.get_directories():
            if reset_flag:
                number = options.get_start()
            if os.path.isdir(directory):
                os.chdir(directory)
                file_stats = []
                for file in glob.glob('*.*'):
                    if os.path.splitext(file)[1].lower() in images_extensions:
                        file_stats.append(file_mod.FileStat(file))
                newfiles = []
                for file_stat in self._sorted(options, file_stats):
                    extension = os.path.splitext(file_stat.get_file())[1]
                    extension = extension.lower().replace('.jpeg', '.jpg')
                    newfile = f'pic{number:05d}{extension}'
                    newfiles.append(newfile)
                    try:
                        shutil.move(
                            file_stat.get_file(),
                            f'pnum.tmp-{newfile}',
                        )
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot rename '
                            f'"{file_stat.get_file()}" image file.',
                        ) from exception
                    number += 1
                for file in newfiles:
                    try:
                        shutil.move(f'pnum.tmp-{file}', file)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot rename to '
                            f'"{file}" image file.',
                        ) from exception
                os.chdir(startdir)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
