#!/usr/bin/env python3
"""
Copy a file to multiple target files.
"""

import argparse
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_source(self) -> str:
        """
        Return source file.
        """
        return os.path.expandvars(self._args.source[0])

    def get_targets(self) -> List[str]:
        """
        Return target files.
        """
        return [os.path.expandvars(x) for x in self._args.targets]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Copy a file to multiple target files.",
        )

        parser.add_argument(
            'source',
            nargs=1,
            help="Source file.",
        )
        parser.add_argument(
            'targets',
            nargs='+',
            metavar='target',
            help="Target file.",
        )

        self._args = parser.parse_args(args)

        if not Path(self._args.source[0]).is_file():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{self._args.source[0]}" file.',
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
    def _copy(path1: Path, path2: Path) -> None:
        if path2.is_dir():
            print(f'Copying to "{Path(path2, path1.name)}" file...')
        else:
            print(f'Copying to "{path2}" file...')
        path_tmp = Path(f'{path2}.part')
        try:
            shutil.copy2(path1, path_tmp)
        except shutil.Error as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{path_tmp}" file.',
            ) from exception
        try:
            path_tmp.replace(path2)
        except OSError:
            try:
                shutil.move(str(path_tmp), str(path2))  # < 3.9
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path2}" file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        source = Path(options.get_source())
        for target in [Path(x) for x in options.get_targets()]:
            self._copy(source, target)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
