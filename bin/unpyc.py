#!/usr/bin/env python3
"""
De-compile PYC file to Python source file.
"""

import argparse
import dis
import marshal
import os
import signal
import struct
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="De-compile PYC file to Python source file.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive (default).",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.pyc',
            help="Python PYC file.",
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
    _pydisasm = command_mod.Command(
        'pydisasm',
        args=['--format=bytes'],
        errors='stop',
    )

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

        os.umask(0o022)

    @staticmethod
    def _dis(path: Path) -> int:
        with path.open('rb') as ifile:
            magic = struct.unpack('h', ifile.read(2))[0]
        # Lib/importlib/_bootstrap_external.py
        if magic <= 3394:
            version = (3, 7)  # 3.7
        elif magic <= 3439:
            version = (3, 10)  # 3.8, 3.9, 3.10
        elif magic <= 3495:
            version = (3, 11)  # 3.11
        elif magic <= 3531:
            version = (3, 12)  # 3.12
        else:
            version = (3, 13)  # 3.13+

        # Run difference version of Python
        if sys.version_info[0:2] != version:
            command = command_mod.Command(
                f'python{version[0]}.{version[1]}',
                args=[__file__, path],
                errors='stop',
            )
            task = subtask_mod.Task(command.get_cmdline())
            task.run()
            return task.get_exitcode()

        print(f"\n# Disassembling: {path}")
        major, minor, micro, *_ = sys.version_info
        print(f"# dis version {major}.{minor}.{micro}")
        print(f"# Python bytecode {version[0]}.{version[1]}.x ({magic})")
        with open(sys.argv[1], "rb") as ifile:
            ifile.read(16)
            dis.dis(marshal.load(ifile))
        return 0

    @classmethod
    def _disasm(cls, path: Path) -> int:
        task = subtask_mod.Batch(cls._pydisasm.get_cmdline() + [path])
        task.run(error2output=True)
        if task.get_exitcode():
            return cls._dis(path)

        print(f"\n# Disassembling: {path}")
        for line in task.get_output():
            print(line)
        return task.get_exitcode()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        paths = [Path(x) for x in options.get_files()]

        return sum(cls._disasm(x) for x in paths if x.suffix == '.pyc')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
