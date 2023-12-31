#!/usr/bin/env python3
"""
Print lines matching a pattern in compressed files.
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def get_ignore_case_flag(self) -> bool:
        """
        Return ignore case flag.
        """
        return self._args.ignoreCase_flag

    def get_invert_flag(self) -> bool:
        """
        Return invert regular expression flag.
        """
        return self._args.invert_flag

    def get_number_flag(self) -> bool:
        """
        Return line number flag.
        """
        return self._args.number_flag

    def get_pattern(self) -> str:
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Print lines matching a pattern.",
        )

        parser.add_argument(
            '-i',
            dest='ignoreCase_flag',
            action='store_true',
            help="Ignore case distinctions.",
        )
        parser.add_argument(
            '-n',
            dest='number_flag',
            action='store_true',
            help="Prefix each line of output with line number.",
        )
        parser.add_argument(
            '-v',
            dest='invert_flag',
            action='store_true',
            help="Invert the sense of matching.",
        )
        parser.add_argument(
            'pattern',
            nargs=1,
            help="Regular expression.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to search.",
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
    zcat = command_mod.Command('zcat', errors='stop')
    grep = command_mod.Command('grep', errors='stop')

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

    @classmethod
    def _file(cls, grep: List[str], file: str, prefix: str = '') -> None:
        cmdline = cls.zcat.get_cmdline() + [file, '|'] + grep
        if prefix:
            cmdline.extend(['|', 'sed', '-e', f's@^@{prefix}@'])
        subtask_mod.Task(cmdline).run()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        grep = cls.grep.get_cmdline()
        if options.get_ignore_case_flag():
            grep.append('-i')
        if options.get_invert_flag():
            grep.append('-v')
        if options.get_number_flag():
            grep.append('-n')
        grep.append(options.get_pattern())

        if len(options.get_files()) > 1:
            for file in options.get_files():
                cls._file(grep, file, prefix=f'{file}:')
        else:
            cls._file(grep, options.get_files()[0])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
