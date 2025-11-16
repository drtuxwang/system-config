#!/usr/bin/env python3
"""
De-compile Python PYC bytecode file.
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

from command_mod import Command
from subtask_mod import Batch, Task


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
            description="De-compile Python PYC bytecode file.",
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
    _pydisasm = Command(
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
        """
        Disassemble using dis
        """
        with path.open('rb') as ifile:
            magic = struct.unpack('h', ifile.read(2))[0]
        # lib/importlib/_bootstrap_external.py
        if magic < 3400:
            version = (3, 7)   # 3.7 and older
        elif magic < 3450:
            version = (3, 10)  # 3.8, 3.9, 3.10
        elif magic < 3500:
            version = (3, 11)  # 3.11
        elif magic < 3550:
            version = (3, 12)  # 3.12
        elif magic < 3600:
            version = (3, 13)  # 3.13
        elif magic < 3650:
            version = (3, 14)  # 3.14
        elif magic < 3700:
            version = (3, 26)  # 3.15(3.26)
        elif magic < 3750:
            version = (3, 27)  # 3.16(3.27)
        else:
            version = (3, 28)  # 3.17(3.28) and later

        # Run difference version of Python
        if sys.version_info[0:2] != version:
            command = Command(
                f'python{version[0]}.{version[1]}',
                args=[__file__, path],
                errors='stop',
            )
            task = Task(command.get_cmdline())
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
        """
        Disassemble using xdis
        """
        task = Batch(cls._pydisasm.get_cmdline() + [path])
        task.run(error2output=True)
        if task.get_exitcode():
            return cls._dis(path)  # fallback method

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
