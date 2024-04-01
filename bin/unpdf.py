#!/usr/bin/env python3
"""
Unpack PDF file into series of JPG files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Task


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

    def get_gs(self) -> Command:
        """
        Return gs Command class object.
        """
        return self._gs

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack PDF file into series of JPG files.",
        )

        parser.add_argument(
            '-dpi',
            nargs=1,
            type=int,
            default=[300],
            help="Selects DPI resolution (default is 300).",
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.pdf',
            help="PDF document file.",
        )

        self._args = parser.parse_args(args)

        if self._args.dpi[0] < 50:
            raise SystemExit(
                f'{sys.argv[0]}: DPI resolution must be at least 50.',
            )

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gs = Command('gs', errors='stop')
        self._gs.set_args([
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-sDEVICE=jpeg',
            f'-r{self._args.dpi[0]}',
        ])


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
        view_flag = options.get_view_flag()

        command = options.get_gs()

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" PDF file.',
                )
            prefix = path.stem
            print(f'Unpacking "{prefix}-page*.jpg" file...')
            file = '/dev/null' if view_flag else f'{prefix}-page%02d.jpg'
            task = Task(command.get_cmdline() + [
                f'-sOutputFile={file}',
                '-c',
                'save',
                'pop',
                '-f',
                str(path),
            ])
            task.run(pattern='Ghostscript|^Copyright|WARRANTY:|^Processing')
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
