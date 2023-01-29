#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.LZMA format.
"""

import argparse
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
            description="Unpack a compressed archive in TAR.LZMA format.",
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
            metavar='file.tar.lzma|file.tlz',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

        for path in [Path(x) for x in self._args.archives]:
            if not path.name.endswith(('.tar.lzma', '.tlz')):
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

        os.umask(0o022)

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        tar = command_mod.Command('tar', errors='stop')
        if options.get_view_flag():
            tar.set_args(['tfv'])
        else:
            tar.set_args(['xfv'])
        task = subtask_mod.Batch(tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        if task.has_output():
            tar.extend_args(['--xattrs', '--xattrs-include=*'])

        for file in options.get_archives():
            print(f"{file}:")
            subtask_mod.Task(tar.get_cmdline() + [file]).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
