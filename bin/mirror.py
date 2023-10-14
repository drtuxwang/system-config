#!/usr/bin/env python3
"""
Copy all files/directory inside a directory into mirror directory.
"""

import argparse
import logging
import os
import shutil
import signal
import sys
import time
from pathlib import Path
from typing import Any, List

import file_mod
import logging_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_mirrors(self) -> List[list]:
        """
        Return list of mirroring directory pair tuples.
        """
        return self._mirrors

    def get_quiet_flag(self) -> bool:
        """
        Return quiet flag.
        """
        return self._args.quiet_flag

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_remove_flag(self) -> bool:
        """
        Return remove flag.
        """
        return self._args.remove_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Copy all files/directory inside a directory "
            "into mirror directory.",
        )

        parser.add_argument(
            '-q',
            dest='quiet_flag',
            action='store_true',
            help="Do not show missing file/directory warnings.",
        )
        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Mirror directories recursively.",
        )
        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help="Delete obsolete files in target directory.",
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='source_dir target_dir',
            help="Source and target directory pairs.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        directories = [os.path.expandvars(x) for x in self._args.directories]
        if len(directories) % 2:
            raise SystemExit(
                f"{sys.argv[0]}: Source and target directory pair has missing "
                "target directory.",
            )
        self._mirrors = []
        for i in range(0, len(directories), 2):
            if not Path(directories[i]).is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Source directory '
                    f'"{directories[i]}" does not exist.',
                )
            self._mirrors.append([directories[i], directories[i+1]])


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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def _automount(directory: str, wait: int) -> None:
        if directory.startswith('/media/'):
            for _ in range(wait * 10):
                if Path(directory).is_dir():
                    break
                time.sleep(0.1)

    @staticmethod
    def _report_old_files(
        source_path: Path,
        source_paths: List[Path],
        target_paths: List[Path],
    ) -> None:
        for target_path in target_paths:
            if Path(source_path, target_path.name) not in source_paths:
                if target_path.is_symlink():
                    logger.warning('No source for "%s" link.', target_path)
                elif target_path.is_dir():
                    logger.warning(
                        'No source for "%s" directory.',
                        target_path
                    )
                else:
                    logger.warning('No source for "%s" file.', target_path)

    def _get_stats(self) -> str:
        elapsed = time.time() - self._start
        copied = self._size/1024
        return f"{int(copied)}/{int(elapsed)}={int(copied/elapsed)}"

    def _remove_old_files(
        self,
        source_path: Path,
        source_paths: List[Path],
        target_paths: List[Path],
    ) -> None:
        for target_path in target_paths:
            if Path(source_path, target_path.name) not in source_paths:
                if target_path.is_symlink():
                    try:
                        os.remove(target_path)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot remove '
                            f'"{target_path}" link.',
                        ) from exception
                elif target_path.is_dir():
                    if self._recursive:
                        logger.warning(
                            '[%s] Removing "%s" directory',
                            self._get_stats(),
                            target_path,
                        )
                        try:
                            shutil.rmtree(target_path)
                        except OSError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Cannot remove '
                                f'"{target_path}" directory.',
                            ) from exception
                else:
                    logger.warning(
                        '[%s] Removing "%s" file.',
                        self._get_stats(),
                        target_path,
                    )
                    try:
                        target_path.unlink()
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot remove '
                            f'"{target_path}" file.',
                        ) from exception

    def _mirror_link(self, source_path: Path, target_path: Path) -> None:
        source_link = source_path.readlink()  # type: ignore

        if target_path.is_symlink():
            target_link = target_path.readlink()  # type: ignore
            if target_link == source_link:
                return
            target_path.unlink()
            logger.info(
                '[%s] Updating "%s" link.',
                self._get_stats(),
                target_path,
            )
        elif target_path.exists():
            try:
                if target_path.is_dir() and not target_path.is_symlink():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove "{target_path}" link.',
                ) from exception
        else:
            logger.info(
                '[%s] Creating "%s" link.',
                self._get_stats(),
                target_path,
            )
        try:
            target_path.symlink_to(source_link)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{target_path}" link.',
            ) from exception
        file_stat = file_mod.FileStat(source_path, follow_symlinks=False)
        file_time = file_stat.get_time()
        try:
            os.utime(
                target_path,
                (file_time, file_time),
                follow_symlinks=False,
            )
        except (FileNotFoundError, NotImplementedError, PermissionError):
            pass

    def _mirror_file(self, source_path: Path, target_path: Path) -> None:
        if target_path.is_symlink():
            try:
                target_path.unlink()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove "{target_path}" link.',
                ) from exception
        elif target_path.is_file():
            source_stat = file_mod.FileStat(source_path)
            target_stat = file_mod.FileStat(target_path)
            if source_stat.get_size() == target_stat.get_size():
                # Allow FAT16/FAT32/NTFS 1h daylight saving
                # and 1 sec rounding error
                if int(
                    abs(source_stat.get_time() - target_stat.get_time())
                ) in (0, 1, 3599, 3600, 3601):
                    if source_stat.get_mode() != target_stat.get_mode():
                        logger.info(
                            '[%s] Updating "%s" permissions.',
                            self._get_stats(),
                            target_path,
                        )
                        try:
                            target_path.chmod(source_stat.get_mode())
                        except OSError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Cannot update '
                                f'"{target_path}" permissions.',
                            ) from exception
                    return
            logger.info(
                '[%s] Updating "%s" file.',
                self._get_stats(),
                target_path,
            )
        else:
            logger.info(
                '[%s] Creating "%s" file.',
                self._get_stats(),
                target_path,
            )
        self._size += int((source_path.stat().st_size + 1023) / 1024)
        try:
            shutil.copy2(source_path, target_path)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with source_path.open(errors='replace'):
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create '
                            f'"{target_path}" file.',
                        ) from exception
                except OSError as exception2:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{target_path}" file.',
                    ) from exception2

    @staticmethod
    def _mirror_directory_time(source_path: Path, target_path: Path) -> None:
        source_time = int(Path(source_path).stat().st_mtime)
        target_time = int(Path(target_path).stat().st_mtime)
        if source_time != target_time:
            try:
                os.utime(target_path, (source_time, source_time))
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update '
                    f'"{target_path}" directory modification time.',
                ) from exception

    def _mirror(self, path1: Path, path2: Path) -> None:
        try:
            source_paths = sorted(path1.iterdir())
        except (OSError, PermissionError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{path1}" source directory.',
            ) from exception
        if path2.is_dir() and not path2.is_symlink():
            try:
                target_paths = sorted(path2.iterdir())
            except (OSError, PermissionError) as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot open "{path2}" target directory.',
                ) from exception
        else:
            target_paths = []
            logger.info(
                '[%s] Creating "%s" directory.',
                self._get_stats(),
                path2,
            )
            try:
                if path2.is_symlink():
                    path2.unlink()
                path2.mkdir(mode=file_mod.FileStat(path1).get_mode())
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path2}" directory.',
                ) from exception

        for source_path in source_paths:
            target_path = Path(path2, Path(source_path).name)
            if source_path.is_symlink():
                self._mirror_link(source_path, target_path)
            elif source_path.is_file():
                self._mirror_file(source_path, target_path)
            elif source_path.is_dir() and self._recursive:
                self._mirror(source_path, target_path)

        if self._options.get_remove_flag():
            self._remove_old_files(path1, source_paths, target_paths)
        elif not self._options.get_quiet_flag():
            self._report_old_files(path1, source_paths, target_paths)

        self._mirror_directory_time(path1, path2)

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        self._recursive = self._options.get_recursive_flag()
        self._size = 0
        self._start = int(time.time())
        for mirror in self._options.get_mirrors():
            self._automount(mirror[1], 8)
            self._mirror(Path(mirror[0]), Path(mirror[1]).resolve())
        logger.info('[%s] Finished!', self._get_stats())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
