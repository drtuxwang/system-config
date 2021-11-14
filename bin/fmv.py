#!/usr/bin/env python3
"""
Move or rename files.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_overwrite_flag(self) -> bool:
        """
        Return overwrite flag.
        """
        return self._args.overwrite_flag

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
        parser = argparse.ArgumentParser(description="Move or rename files.")

        parser.add_argument(
            '-f',
            dest='overwrite_flag',
            action='store_true',
            help="Overwrite files.",
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

    def _move(self) -> None:
        if not os.path.isdir(self._options.get_target()):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._options.get_target()}" target directory.',
            )
        for source in self._options.get_sources():
            if os.path.isdir(source):
                print(f'Moving "{source}" directory...')
            elif os.path.isfile(source):
                print(f'Moving "{source}" file...')
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find '
                    f'"{source}" source file or directory.',
                )
            target = os.path.join(
                self._options.get_target(), os.path.basename(source))
            if os.path.isdir(target):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot safely overwrite '
                    f'"{target}" target directory.',
                )
            if os.path.isfile(target):
                if not self._options.get_overwrite_flag():
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot safely overwrite '
                        f'"{target}" target file.',
                    )
            try:
                shutil.move(source, target)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot move "{source}" source file.',
                ) from exception

    def _rename(self, source: str, target: str) -> None:
        if os.path.isdir(source):
            print(f'Renaming "{source}" directory...')
        elif os.path.isfile(source):
            print(f'Renaming "{source}" file...')
        else:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{source}" source file or directory.',
            )
        if os.path.isdir(target):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot safely overwrite '
                f'"{target}" target directory.',
            )
        if os.path.isfile(target):
            if not self._options.get_overwrite_flag():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot safely overwrite '
                    f'"{target}" target file.',
                )

        try:
            shutil.move(source, target)
        except OSError as exception:
            if os.path.isdir(source):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot rename '
                    f'"{source}" source directory.',
                ) from exception
            raise SystemExit(
                f'{sys.argv[0]}: Cannot rename "{source}" source file.',
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        sources = self._options.get_sources()
        target = self._options.get_target()

        if len(sources) > 1 or os.path.isdir(target):
            self._move()
        else:
            self._rename(sources[0], target)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
