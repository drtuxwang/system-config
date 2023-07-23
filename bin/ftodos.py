#!/usr/bin/env python3
"""
Converts file to '\r\n' newline format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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
        return [os.path.expandvars(x) for x in self._args.files]

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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')
            print(f'Converting "{path}" file to "\\r\\n" newline format...')
            try:
                with path.open(errors='replace') as ifile:
                    path_new = Path(f'{path}.part')
                    try:
                        with path_new.open('w', newline='\r\n') as ofile:
                            for line in ifile:
                                print(line.rstrip('\r\n'), file=ofile)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create "{path_new}" file.',
                        ) from exception
                    except UnicodeDecodeError as exception:
                        path_new.unlink()
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot convert '
                            f'"{path}" binary file.',
                        ) from exception
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{path}" file.',
                ) from exception
            try:
                path_new.replace(path)
            except OSError as exception:
                path_new.unlink()
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update "{path}" file.',
                ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
