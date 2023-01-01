#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.7Z format.
"""

import argparse
import glob
import os
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

    def get_archives(self) -> List[str]:
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in TAR.7Z format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.tar.7z|file.t7z',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

        for path in [Path(x) for x in self._args.archives]:
            if not path.name.endswith(('.tar.7z', '.t7z')):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsupported "{path}" archive format.',
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _unpack(self, file: str) -> None:
        unpacker = command_mod.Command('7z', errors='stop')
        unpacker.set_args(['x', '-so', file])
        self._tar.set_args(['xfv', '-'])
        task = subtask_mod.Batch(self._tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        if task.has_output():
            self._tar.extend_args(['--xattrs', '--xattrs-include=*'])
        subtask_mod.Task(
            unpacker.get_cmdline() + ['|'] + self._tar.get_cmdline()
        ).run()

    def _view(self, file: str) -> None:
        unpacker = command_mod.Command('7z', errors='stop')
        unpacker.set_args(['x', '-so', file])
        self._tar.set_args(['tfv', '-'])
        task = subtask_mod.Batch(self._tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        if task.has_output():
            self._tar.extend_args(['--xattrs', '--xattrs-include=*'])
        subtask_mod.Task(
            unpacker.get_cmdline() + ['|'] + self._tar.get_cmdline()
        ).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(0o022)
        if os.name == 'nt':
            self._tar = command_mod.Command('tar.exe', errors='stop')
        else:
            self._tar = command_mod.Command('tar', errors='stop')

        for file in options.get_archives():
            print(f"{file}:")
            if options.get_view_flag():
                self._view(file)
            else:
                self._unpack(file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
