#!/usr/bin/env python3
"""
Unpack a compressed DMG disk file.
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
        Return list of disk files.
        """
        return self._args.files

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed DMG disk file.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of disk file.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.dmg',
            help="Disk file.",
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        dmg2img = command_mod.Command('dmg2img', errors='stop')
        p7zip = command_mod.Command('7z', errors='stop')
        if options.get_view_flag():
            p7zip.set_args(['l'])
        else:
            p7zip.set_args(['x', '-y'])

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" disk file.',
                )
            print(f"{file}:")
            task = subtask_mod.Task(
                dmg2img.get_cmdline() + [file, 'dmg2img.img'])
            task.run()

            task = subtask_mod.Task(p7zip.get_cmdline() + ['dmg2img.img'])
            task.run()
            try:
                os.remove('dmg2img.img')
            except OSError:
                pass
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {str(task.get_exitcode())} '
                    f'received from "{task.get_file()}".',
                )
        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
