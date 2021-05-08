#!/usr/bin/env python3
"""
Zero device or create zero file.
"""

import argparse
import glob
import os
import signal
import sys
import time
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
        return self._args.location[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Zero device or create zero file.',
        )

        parser.add_argument(
            'location',
            nargs=1,
            metavar='device|directory',
            help='Device to zero or directory to create "fzero.tmp" file.'
        )

        self._args = parser.parse_args(args)

        location = self._args.location[0]
        if os.path.exists(location):
            if os.path.isfile(location):
                raise SystemExit(
                    sys.argv[0] + ': Cannot zero existing "' +
                    location + '" file.'
                )
        else:
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + location +
                '" device or directory.'
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        if os.path.isdir(options.get_location()):
            file = os.path.join(options.get_location(), 'fzero.tmp')
            print('Creating "' + file + '" zero file...')
        else:
            file = options.get_location()
            print('Zeroing "' + file + '" device...')
        start_time = time.time()
        chunk = 16384 * b'\0'
        size = 0
        try:
            with open(file, 'wb') as ofile:
                while True:
                    for _ in range(64):
                        ofile.write(chunk)
                    size += 1
                    sys.stdout.write("\r{0:d} MB".format(size))
                    sys.stdout.flush()
        except (KeyboardInterrupt, OSError):
            pass
        elapsed_time = time.time() - start_time
        print(", {0:4.2f} seconds, {1:.0f} MB/s".format(
            elapsed_time, size / elapsed_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
