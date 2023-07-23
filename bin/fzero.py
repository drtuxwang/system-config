#!/usr/bin/env python3
"""
Zero device or create zero file.
"""

import argparse
import os
import signal
import sys
import time
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_location(self) -> str:
        """
        Return location.
        """
        return os.path.expandvars(self._args.location[0])

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Zero device or create zero file.",
        )

        parser.add_argument(
            'location',
            nargs=1,
            metavar='device|directory',
            help='Device to zero or directory to create "fzero.tmp" file.',
        )

        self._args = parser.parse_args(args)

        location = Path(self._args.location[0])
        if location.exists():
            if location.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot zero existing "{location}" file.',
                )
        else:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{location}" device or directory.'
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        if Path(options.get_location()).is_dir():
            path = Path(options.get_location(), 'fzero.tmp')
            print(f'Creating "{path}" zero file...')
        else:
            path = Path(options.get_location())
            print(f'Zeroing "{path}" device...')
        start_time = time.time()
        chunk = 16384 * b'\0'
        size = 0
        try:
            with path.open('wb') as ofile:
                while True:
                    for _ in range(64):
                        ofile.write(chunk)
                    size += 1
                    sys.stdout.write(f"\r{size} MB")
                    sys.stdout.flush()
        except (KeyboardInterrupt, OSError):
            pass
        elapsed_time = time.time() - start_time
        print(f", {elapsed_time:4.2f} seconds, {size / elapsed_time:.0f} MB/s")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
