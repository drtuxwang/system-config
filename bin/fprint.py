#!/usr/bin/env python3
"""
Send text/images/postscript/PDF files to browser for printing.
"""

import argparse
import os
import shutil
import signal
import sys
import time
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileUtil
from subtask_mod import Batch, Daemon, Task


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
            description="Send files to browser for printing.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="A text/images/postscript/PDF file.",
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
        sys.exit(0)

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
    def _print(files: List[str]) -> None:
        tmpdir = FileUtil.tmpdir(Path('.cache', 'fprint'))
        pdf = Command('pdf', errors='stop')
        xweb = Command('xweb', errors='stop')
        task: Task

        for number, file in enumerate(files):
            if not Path(file).is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" file.',
                )

            tmpfile = f"{tmpdir}/{number:02d}.pdf"
            task = Batch(pdf.get_cmdline() + [tmpfile, file])
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f"{sys.argv[0]}: Cannot convert to PDF: {file}",
                )

            print(f"Sending to browser for printing: {file}")
            task = Daemon(xweb.get_cmdline() + [tmpfile])
            task.run()
            time.sleep(0.5)

        time.sleep(2)
        shutil.rmtree(tmpdir)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        cls._print(options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
