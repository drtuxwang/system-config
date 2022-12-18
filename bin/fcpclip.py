#!/usr/bin/env python3
"""
Copy file from clipboard location.
"""

import argparse
import shutil
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directory(self) -> str:
        """
        Return directory.
        """
        return self._args.directory[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Copy file from clipboard location to directory.",
        )

        parser.add_argument(
            'directory',
            nargs=1,
            help="Directory to copy file.",
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        xclip = command_mod.Command('xclip', errors='stop')
        xclip.set_args(['-out', '-selection', '-c', 'test'])
        task = subtask_mod.Batch(xclip.get_cmdline())
        task.run()

        source = ''.join(task.get_output())
        if Path(source).is_file():
            directory = Path(options.get_directory())
            target_path = Path(directory, Path(source).name)
            print(f'Copying "{source}" file to "{target_path}"...')
            try:
                if not directory.is_dir():
                    directory.mkdir(parents=True)
                shutil.copy2(source, target_path)
            except (OSError, shutil.Error) as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot copy to "{target_path}" file.',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
