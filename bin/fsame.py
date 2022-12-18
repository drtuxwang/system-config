#!/usr/bin/env python3
"""
Show files with same MD5 checksums.
"""

import argparse
import glob
import hashlib
import logging
import os
import signal
import sys
from pathlib import Path
from typing import List

import logging_mod
import command_mod

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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

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
            description="Show files with same MD5 checksums.",
        )

        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help="Delete all extra copies of duplicated files.",
        )
        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|file.md5',
            help='File to checksum or ".md5" checksum file.'
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

    def _calc(self, options: Options, paths: List[Path]) -> None:
        for path in paths:
            if path.is_dir():
                if not path.is_symlink() and options.get_recursive_flag():
                    try:
                        self._calc(options, sorted(
                            [Path(path, x.name) for x in path.iterdir()]
                        ))
                    except PermissionError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot open "{path}" directory.',
                        ) from exception
            elif path.is_file():
                md5sum = self._md5sum(path)
                if not md5sum:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{path}" file.',
                    )
                if md5sum in self._md5files:
                    self._md5files[md5sum].add(path)
                else:
                    self._md5files[md5sum] = set([path])

    @staticmethod
    def _md5sum(path: Path) -> str:
        try:
            with path.open('rb') as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (OSError, TypeError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.',
            ) from exception
        return md5.hexdigest()

    @staticmethod
    def _remove(paths: List[Path]) -> None:
        for path in paths:
            print(f'  Removing "{path}" duplicated file')
            try:
                path.unlink()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove "{path}" file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._md5files: dict = {}
        paths = []
        for path in [Path(x) for x in options.get_files()]:
            if path.is_dir():
                paths.extend(sorted(path.iterdir()))
            else:
                paths.append(path)
        self._calc(options, paths)

        exitcode = 0
        for paths in sorted(self._md5files.values()):
            if len(paths) > 1:
                sorted_paths = sorted(paths)
                logger.warning(
                    "Identical: %s",
                    command_mod.Command.args2cmd([
                        str(x) for x in sorted_paths
                    ])
                )
                if options.get_remove_flag():
                    self._remove(sorted_paths[1:])
                else:
                    exitcode = 1
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
