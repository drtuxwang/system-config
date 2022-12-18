#!/usr/bin/env python3
"""
Check for missing sequence in numbered files.
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple


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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Check for missing sequence in numbered files.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to check.",
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
    def _check_missing(seq_name: Tuple[str, str], numbers: List[int]) -> None:
        sequence = set(range(min(numbers), max(numbers)+1))
        name, ext = seq_name
        for missing in sorted(sequence - set(numbers)):
            print(f"Missing file in sequence: {name}_{missing:03d}{ext}")

    @classmethod
    def _check_sequences(cls, files: List[str]) -> None:
        sequences: dict = {}
        for path in [Path(x) for x in files]:
            if '_' in str(path) and path.is_file():
                name, ext = os.path.splitext(str(path))
                name, number = name.rsplit('_', 1)
                seq_name = (name, ext)
                sequences[seq_name] = sequences.get(seq_name, set())
                try:
                    sequences[seq_name].add(int(number))
                except ValueError:
                    pass
            elif path.is_dir():
                cls._check_sequences([str(x) for x in path.glob('*')])

        for seq_name, numbers in sorted(sequences.items()):
            if len(numbers) > 1:
                cls._check_missing(seq_name, numbers)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        cls._check_sequences(options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
