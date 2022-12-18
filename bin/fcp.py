#!/usr/bin/env python3
"""
Copy files and directories.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
import time
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

    def get_sources(self) -> List[str]:
        """
        Return list of source files.
        """
        return self._args.sources

    def get_target(self) -> str:
        """
        Return target file or directory.
        """
        return self._args.target[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Copy files and directories.",
        )

        parser.add_argument(
            'sources',
            nargs='+',
            metavar='source',
            help="Source file or directory.",
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='target',
            help="Target file or directory.",
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _automount(directory: str, wait: int) -> None:
        if directory.startswith('/media/'):
            for _ in range(0, wait * 10):
                if Path(directory).is_dir():
                    break
                time.sleep(0.1)

    @staticmethod
    def _copy_link(path1: Path, path2: Path) -> None:
        print(f'Creating "{path2}" link...')
        source_link = path1.readlink()

        if path2.is_symlink():
            target_link = path2.readlink()
            if target_link == source_link:
                return
        elif path2.is_file():
            try:
                path2.unlink()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove "{path2}" link.',
                ) from exception

        try:
            path2.symlink_to(source_link)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{path2}" link.',
            ) from exception
        file_stat = file_mod.FileStat(path1, follow_symlinks=False)
        file_time = file_stat.get_time()
        try:
            os.utime(path2, (file_time, file_time), follow_symlinks=False)
        except NotImplementedError:
            pass

    def _copy_directory(self, path1: Path, path2: Path) -> None:
        print(f'Creating "{path2}" directory...')
        try:
            paths = sorted(path1.iterdir())
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{path1}" directory.',
            ) from exception
        if not path2.is_dir():
            try:
                path2.mkdir(
                    mode=file_mod.FileStat(path1).get_mode(),
                    parents=True,
                )
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path2}" directory.',
                ) from exception
        for path in paths:
            self._copy(path, Path(path2, path.name))
        newest = file_mod.FileUtil.newest(list(path2.iterdir()))
        if not newest:
            newest = str(path1)
        file_stat = file_mod.FileStat(newest, follow_symlinks=False)
        file_time = file_stat.get_time()
        os.utime(path2, (file_time, file_time))

    @staticmethod
    def _copy_file(path1: Path, path2: Path) -> None:
        print(f'Creating "{path2}" file...')
        try:
            shutil.copy2(path1, path2)
        except shutil.Error as exception:
            if 'are the same file' in exception.args[0]:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot copy to same "{path2}" file.',
                ) from exception
            raise SystemExit(
                f'{sys.argv[0]}: Cannot copy to "{path2}" file.',
            ) from exception
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with path1.open('rb'):
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create "{path2}" file.',
                        ) from exception
                except OSError as exception2:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{path2}" file.',
                    ) from exception2

    def _copy(self, path1: Path, path2: Path) -> None:
        if path1.is_symlink():
            self._copy_link(path1, path2)
        elif path1.is_dir():
            self._copy_directory(path1, path2)
        elif path1.is_file():
            self._copy_file(path1, path2)

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        sources = self._options.get_sources()
        target = self._options.get_target()
        self._automount(target, 8)

        if len(sources) == 1:
            if not Path(target).is_dir():
                self._copy_file(Path(sources[0]), Path(target))
                return 0
        elif not Path(target).is_dir():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{target}" target directory.',
            )

        for source in sources:
            if Path(source).is_dir():
                if (
                    Path(source).is_absolute or
                    source.split(os.sep)[0] in (os.curdir, os.pardir)
                ):
                    self._copy(Path(source), Path(target, Path(source).name))
                else:
                    path = Path(target, source).parent
                    if not path.is_dir():
                        try:
                            path.mkdir(
                                mode=file_mod.FileStat(source).get_mode(),
                                parents=True,
                            )
                        except OSError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Cannot create '
                                f'"{path}" directory.',
                            ) from exception
                    self._copy(Path(source), Path(target, source))
            else:
                path = Path(target, Path(source).parent)
                if not path.is_dir():
                    try:
                        path.mkdir(parents=True)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create '
                            f'"{path}" directory.',
                        ) from exception
                self._copy(Path(source), Path(target, source))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
