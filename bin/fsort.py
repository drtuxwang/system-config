#!/usr/bin/env python3
"""
Unicode sort lines of a file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import LooseVersion


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_order(self) -> str:
        """
        Return display order.
        """
        return self._args.order

    def get_reverse_flag(self) -> bool:
        """
        Return reverse flag.
        """
        return self._args.reverse_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unicode sort lines of a file.",
        )

        parser.add_argument(
            '-v',
            action='store_const',
            const='version',
            dest='order',
            default='unicode',
            help="Sort lines as loose versions."
        )
        parser.add_argument(
            '-r',
            dest='reverse_flag',
            action='store_true',
            help="Reverse order."
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File contents to sort.",
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

        lines = []
        if options.get_files():
            for file in options.get_files():
                try:
                    with Path(file).open(errors='replace') as ifile:
                        for line in ifile:
                            line = line.rstrip('\n')
                            lines.append(line)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{file}" file.',
                    ) from exception
        else:
            for line in sys.stdin:
                lines.append(line.rstrip('\n'))

        if options.get_order() == 'version':
            lines = sorted(
                lines,
                key=lambda  # pylint: disable=unnecessary-lambda
                s: LooseVersion(s),
            )
        else:
            lines = sorted(lines)
        if options.get_reverse_flag():
            lines = reversed(lines)  # type: ignore

        for line in lines:
            print(line)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
