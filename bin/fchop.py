#!/usr/bin/env python3
"""
Chop up a file into chunks.
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import BinaryIO, List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_file(self) -> str:
        """
        Return file.
        """
        return self._args.file[0]

    def get_max_size(self) -> int:
        """
        Return max size of file part.
        """
        return self._max_size

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Chop up a file into chunks.",
        )

        parser.add_argument(
            'file',
            nargs=1,
            help="File to break up.",
        )
        parser.add_argument(
            'size',
            nargs=1,
            metavar='bytes',
            help="Maximum chunk size in bytes or MB.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        try:
            size = self._args.size[0]
            if size.endswith('MB'):
                self._max_size = int(size[:-2]) * 1024**2
            else:
                self._max_size = int(size)
        except ValueError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific an integer for chunksize.',
            ) from exception
        if self._max_size < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer '
                'for chunksize.',
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _copy(self, ifile: BinaryIO, ofile: BinaryIO) -> None:
        chunks, lchunk = divmod(self._max_size, self._cache_size)
        for i in [self._cache_size]*chunks + [lchunk]:
            chunk = ifile.read(i)
            if not chunk:
                break
            ofile.write(chunk)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        self._cache_size = 131072
        self._max_size = options.get_max_size()

        try:
            with open(options.get_file(), 'rb') as ifile:
                for part in range(int(
                    Path(options.get_file()).stat().st_size /
                    options.get_max_size() + 1
                )):
                    try:
                        file = f'{options.get_file()}.{str(part + 1).zfill(3)}'
                        with open(file, 'wb') as ofile:
                            print(f"{file}...")
                            self._copy(ifile, ofile)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create '
                            f'"{str(part + 1).zfill(3)}" file.',
                        ) from exception
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{options.get_file()}" file.',
            ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
