#!/usr/bin/env python3
"""
Dump the first and last few bytes of a binary file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_all_flag(self) -> bool:
        """
        Return all flag.
        """
        return self._args.all_flag

    def get_ascii_flag(self) -> bool:
        """
        Return ascii flag.
        """
        return self._args.ascii_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Dump the first and last few bytes of a binary file.",
        )

        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help="Show contents of the whole file.",
        )
        parser.add_argument(
            '-c',
            dest='ascii_flag',
            action='store_true',
            help="Show contents as ASCII characters.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to view.",
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _format(options: Options, data: bytes) -> str:
        if options.get_ascii_flag():
            line = ' '
            for byte in data:
                if 31 < byte < 127:
                    line += f'   {chr(byte)}'
                elif byte == 10:
                    line += r'  \n'
                elif byte == 13:
                    line += r'  \r'
                else:
                    line += f' {str(byte).zfill(3)}'
        else:
            line = ' '
            for byte in data:
                line += f' {str(byte).rjust(3)}'
        return line

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            try:
                with path.open('rb') as ifile:
                    print(f"\nFile: {path}")
                    file_stat = file_mod.FileStat(path)
                    if options.get_all_flag() or file_stat.get_size() < 128:
                        for position in range(1, file_stat.get_size() + 1, 16):
                            print(
                                f"{position:07d}"
                                f"{self._format(options, ifile.read(16))}",
                            )
                    else:
                        for position in range(1, 65, 16):
                            print(
                                f"{position:07d}"
                                f"{self._format(options, ifile.read(16))}",
                            )
                        print("...")
                        ifile.seek(file_stat.get_size() - 64)
                        for position in range(
                                file_stat.get_size() - 63,
                                file_stat.get_size() + 1,
                                16
                        ):
                            print(
                                f"{position:07d}"
                                f"{self._format(options, ifile.read(16))}",
                            )
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{path}" file.',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
