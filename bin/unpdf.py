#!/usr/bin/env python3
"""
Unpack PDF file into series of JPG files.
"""

import argparse
import glob
import os
import signal
import sys
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_gs(self) -> command_mod.Command:
        """
        Return gs Command class object.
        """
        return self._gs

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

        self._gs = command_mod.Command('gs', errors='stop')
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

        command = options.get_gs()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" PDF file.',
                )
            prefix = os.path.basename(file).rsplit('.', 1)[0]
            print(f'Unpacking "{prefix}-page*.jpg" file...')
            task = subtask_mod.Task(command.get_cmdline() + [
                f'-sOutputFile={prefix}-page%02d.jpg',
                '-c',
                'save',
                'pop',
                '-f',
                file
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
