#!/usr/bin/env python3
"""
Move or rename files.
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

        target = self._args.target[0]
        if target.endswith('/') and not Path(target).exists():
            try:
                Path(target).mkdir(parents=True)
            except OSError:
                pass


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

    def _move(self) -> None:
        if not Path(self._options.get_target()).is_dir():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._options.get_target()}" target directory.',
            )
        for source_path in [Path(x) for x in self._options.get_sources()]:
            if source_path.is_dir():
                print(f'Moving "{source_path}" directory...')
            elif source_path.is_file():
                print(f'Moving "{source_path}" file...')
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find '
                    f'"{source_path}" source file or directory.',
                )
            target_path = Path(
                self._options.get_target(),
                Path(source_path).name,
            )
            if target_path.is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot safely overwrite '
                    f'"{target_path}" target directory.',
                )
            if target_path.is_file():
                if not self._options.get_overwrite_flag():
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot safely overwrite '
                        f'"{target_path}" target file.',
                    )
            try:
                source_path.replace(target_path)
            except OSError:
                try:  # retry for moving between devices
                    shutil.move(str(source_path), target_path)  # < 3.9
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot move '
                        f'"{source_path}" source file.',
                    ) from exception

    def _rename(self, source_path: Path, target_path: Path) -> None:
        if source_path.is_dir():
            print(f'Renaming "{source_path}" directory...')
        elif source_path.is_file():
            print(f'Renaming "{source_path}" file...')
        else:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{source_path}" source file or directory.',
            )
        if target_path.is_dir():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot safely overwrite '
                f'"{target_path}" target directory.',
            )
        if target_path.is_file():
            if not self._options.get_overwrite_flag():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot safely overwrite '
                    f'"{target_path}" target file.',
                )

        try:
            if not target_path.parent.exists():
                target_path.parent.mkdir(parents=True)
            source_path.replace(target_path)
        except OSError:
            try:  # retry for moving between devices
                shutil.move(str(source_path), target_path)  # < 3.9
            except OSError as exception:
                if source_path.is_dir():
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot rename '
                        f'"{source_path}" source directory.',
                    ) from exception
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot rename '
                    f'"{source_path}" source file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        sources = self._options.get_sources()
        target_path = Path(self._options.get_target())

        if len(sources) > 1 or target_path.is_dir():
            self._move()
        else:
            self._rename(Path(sources[0]), target_path)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
