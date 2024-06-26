#!/usr/bin/env python3
"""
Unpack a compressed archive in RPM format.
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

    def get_archives(self) -> List[str]:
        """
        Return list of archive files.
        """
        return self._args.archives

    def get_cpio(self) -> Command:
        """
        Return cpio Command class object.
        """
        return self._cpio

    def get_rpm2cpio(self) -> Command:
        """
        Return rpm2cpio Command class object.
        """
        return self._rpm2cpio

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in RPM format.",
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
            metavar='file.rpm',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._rpm2cpio = Command('rpm2cpio', errors='stop')
        self._cpio = Command('cpio', errors='stop')
        if self._args.view_flag:
            self._cpio.set_args(['-idmt', '--no-absolute-filenames'])
        else:
            self._cpio.set_args(['-idmv', '--no-absolute-filenames'])


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

        cpio = options.get_cpio()
        rpm2cpio = options.get_rpm2cpio()

        for archive in [Path(x) for x in options.get_archives()]:
            if not archive.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{archive}" archive file.',
                )
            print(f"{archive}:")
            task = Task(rpm2cpio.get_cmdline() + [
                str(archive),
                '|',
            ] + cpio.get_cmdline())
            task.run()
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
