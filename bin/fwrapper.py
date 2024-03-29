#!/usr/bin/env python3
"""
Create wrapper to run script/executable.
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
            description="Create wrapper to run script/executable.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Script/executable to wrap.",
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
    def _create(path: Path, link_path: Path) -> None:
        try:
            with link_path.open('w') as ofile:
                print("#!/usr/bin/env bash", file=ofile)
                print("#", file=ofile)
                print("# fwrapper.py generated script", file=ofile)
                print("#\n", file=ofile)
                print('MYDIR=$(dirname "$0")', file=ofile)
                print(f'exec "$MYDIR/{path}" "$@"', file=ofile)

            link_path.chmod(0o755)
            file_time = int(path.stat().st_mtime)
            os.utime(link_path, (file_time, file_time))
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{link_path}" wrapper file.',
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._files = options.get_files()
        for path in [Path(x) for x in self._files]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" file.',
                )

            link = Path(path.name.lower().replace(' ', ''))
            if link.exists():
                print(f'Updating "{link}" wrapper for "{path}"...')
            else:
                print(f'Creating "{link}" wrapper for "{path}"...')
            self._create(path, link)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
