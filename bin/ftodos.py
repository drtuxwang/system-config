#!/usr/bin/env python3
"""
Converts file to '\r\n' newline format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
from typing import List


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
            description='Converts file to "\\r\\n" newline format.',
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to change.",
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

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{file}" file.')
            print(f'Converting "{file}" file to "\\r\\n" newline format...')
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    tmpfile = file + '.part'
                    try:
                        with open(
                            tmpfile,
                            'w',
                            encoding='utf-8',
                            newline='\r\n',
                        ) as ofile:
                            for line in ifile:
                                print(line.rstrip('\r\n'), file=ofile)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create "{tmpfile}" file.',
                        ) from exception
                    except UnicodeDecodeError as exception:
                        os.remove(tmpfile)
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot convert '
                            f'"{file}" binary file.',
                        ) from exception
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{file}" file.',
                ) from exception
            try:
                shutil.move(tmpfile, file)
            except OSError as exception:
                os.remove(tmpfile)
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update "{file}" file.',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
