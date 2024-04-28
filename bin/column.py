#!/usr/bin/env python3
"""
Wrapper for "column" command.

Use " " punctuation space (U+2008, 226 128 136) within columns
"""

import os
import re
import signal
import sys
from pathlib import Path
from typing import List, TextIO

from command_mod import Command
from logging_mod import Message
from subtask_mod import Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._files]

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._files = []
        for arg in args[1:]:
            if arg != '-t':
                if arg.startswith('-'):
                    column = Command('column', errors='stop')
                    Exec(column.get_cmdline() + args[1:]).run()
                self._files.append(arg)


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

    def _file(self, file: str) -> None:
        try:
            with Path(file).open(errors='replace') as ifile:
                self._pipe(ifile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" file.',
            ) from exception

    @staticmethod
    def _pipe(pipe: TextIO) -> None:
        issep = re.compile('[\t ]+')

        rows = []
        for line in pipe:
            rows.append([Message(x) for x in issep.split(line.strip())])

        if rows:
            ncol = max(len(x) for x in rows)
            rows = [x + [Message('')]*(ncol - len(x)) for x in rows]
            for col in range(ncol):
                width = max(x[col].width() for x in rows)
                for row in rows:
                    cell = row[col]
                    row[col] = cell.get(width, lpad=cell[:1].isdigit())
            for row in rows:
                print("  ".join(row))

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if len(options.get_files()) > 1:
            for file in options.get_files():
                print("==>", file, "<==")
                self._file(file)
        elif len(options.get_files()) == 1:
            self._file(options.get_files()[0])
        else:
            self._pipe(sys.stdin)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
