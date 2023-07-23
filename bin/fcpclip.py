#!/usr/bin/env python3
"""
Copy file from clipboard location.
"""

import argparse
import os
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
        return self._target

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Copy file from clipboard location to directory.",
        )

        parser.add_argument(
            'target',
            nargs=1,
            help="Directory to copy file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._target = os.path.expandvars(self._args.target[0])
        if self._target.endswith('/') and not Path(self._target).exists():
            try:
                Path(self._target).mkdir(parents=True)
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

        path = Path(os.path.expandvars(''.join(task.get_output())))
        if path.is_file():
            directory = Path(options.get_directory())
            path_new = Path(directory, path.name)
            if path_new.exists():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot safely overwrite '
                    f'"{path_new}" file.',
                )
            print(f'Creating "{path_new}" file...')
            try:
                if not directory.is_dir():
                    directory.mkdir(parents=True)
                shutil.copy2(path, path_new)
            except (OSError, shutil.Error) as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot copy to "{path_new}" file.',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
