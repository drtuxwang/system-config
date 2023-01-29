#!/usr/bin/env python3
"""
Recursively link all files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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

    def _link_files(  # pylint: disable=too-many-branches
        self,
        path1: Path,
        path2: Path,
        subdir: Path = Path(''),
    ) -> None:
        try:
            source_paths = sorted(path1.iterdir())
        except PermissionError:
            return
        if not path2.is_dir():
            print(f'Creating "{path2}" directory...')
            try:
                path2.mkdir()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path2}" directory.',
                ) from exception

        for source_path in source_paths:
            target_path = Path(path2, source_path.name)
            if source_path.is_dir():
                self._link_files(
                    source_path,
                    target_path,
                    Path(os.pardir, subdir)
                )
            else:
                if target_path.is_symlink():
                    print(f'Updating "{target_path}" link...')
                    try:
                        target_path.unlink()
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot remove '
                            f'"{target_path}" link.',
                        ) from exception
                else:
                    print(f'Creating "{target_path}" link...')
                if source_path.is_absolute():
                    path = source_path
                else:
                    path = Path(subdir, source_path)
                try:
                    path.symlink_to(target_path)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{target_path}" link.',
                    ) from exception
                file_stat = file_mod.FileStat(path)
                file_time = file_stat.get_time()
                try:
                    os.utime(
                        target_path,
                        (file_time, file_time),
                        follow_symlinks=False,
                    )
                except NotImplementedError:
                    os.utime(target_path, (file_time, file_time))

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_directories()]:
            self._link_files(path, Path('.'))

        return 0


if '--pydoc' in sys.argv:
    help(__name__)
else:
    Main()
