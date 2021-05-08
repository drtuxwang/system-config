#!/usr/bin/env python3
"""
Dump the first and last few bytes of a binary file.
"""

import argparse
import glob
import os
import signal
import sys
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
            description='Dump the first and last few bytes of a binary file.',
        )

        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help='Show contents of the whole file.'
        )
        parser.add_argument(
            '-c',
            dest='ascii_flag',
            action='store_true',
            help='Show contents as ASCII characters.'
        )
        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='File to view.'
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
    def _format(options: Options, data: bytes) -> str:
        if options.get_ascii_flag():
            line = ' '
            for byte in data:
                if 31 < byte < 127:
                    line += '   ' + chr(byte)
                elif byte == 10:
                    line += r'  \n'
                elif byte == 13:
                    line += r'  \r'
                else:
                    line += ' ' + str(byte).zfill(3)
        else:
            line = ' '
            for byte in data:
                line += ' ' + str(byte).rjust(3)
        return line

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            try:
                with open(file, 'rb') as ifile:
                    print("\nFile:", file)
                    file_stat = file_mod.FileStat(file)
                    if options.get_all_flag() or file_stat.get_size() < 128:
                        for position in range(1, file_stat.get_size() + 1, 16):
                            print("{0:07d}{1:s}".format(
                                position,
                                self._format(options, ifile.read(16))
                            ))
                    else:
                        for position in range(1, 65, 16):
                            print("{0:07d}{1:s}".format(
                                position,
                                self._format(options, ifile.read(16))
                            ))
                        print("...")
                        ifile.seek(file_stat.get_size() - 64)
                        for position in range(
                                file_stat.get_size() - 63,
                                file_stat.get_size() + 1,
                                16
                        ):
                            print("{0:07d}{1:s}".format(
                                position,
                                self._format(options, ifile.read(16))
                            ))
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + file + '" file.'
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
