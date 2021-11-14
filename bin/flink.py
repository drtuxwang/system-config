#!/usr/bin/env python3
"""
Recursively link all files.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Recursively link all files.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing files to link.",
        )

        self._args = parser.parse_args(args)

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

    def _link_files(  # pylint: disable = too-many-branches
        self,
        source_dir: str,
        target_dir: str,
        subdir: str = '',
    ) -> None:
        try:
            source_files = sorted([
                os.path.join(source_dir, x)
                for x in os.listdir(source_dir)
            ])
        except PermissionError:
            return
        if not os.path.isdir(target_dir):
            print(f'Creating "{target_dir}" directory...')
            try:
                os.mkdir(target_dir)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{target_dir}" directory.',
                ) from exception

        for source_file in sorted(source_files):
            target_file = os.path.join(
                target_dir,
                os.path.basename(source_file)
            )
            if os.path.isdir(source_file):
                self._link_files(
                    source_file,
                    target_file,
                    os.path.join(os.pardir, subdir)
                )
            else:
                if os.path.islink(target_file):
                    print(f'Updating "{target_file}" link...')
                    try:
                        os.remove(target_file)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot remove '
                            f'"{target_file}" link.',
                        ) from exception
                else:
                    print(f'Creating "{target_file}" link...')
                if os.path.isabs(source_file):
                    file = source_file
                else:
                    file = os.path.join(subdir, source_file)
                try:
                    os.symlink(file, target_file)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{target_file}" link.',
                    ) from exception
                file_stat = file_mod.FileStat(file)
                file_time = file_stat.get_time()
                try:
                    os.utime(
                        target_file,
                        (file_time, file_time),
                        follow_symlinks=False,
                    )
                except NotImplementedError:
                    os.utime(target_file, (file_time, file_time))

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for directory in options.get_directories():
            self._link_files(directory, '.')

        return 0


if '--pydoc' in sys.argv:
    help(__name__)
else:
    Main()
