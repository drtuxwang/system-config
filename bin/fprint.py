#!/usr/bin/env python3
"""
Send text/images/postscript/PDF files to browser for printing.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
import time
from typing import List

import command_mod
import file_mod
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
        return self._args.files

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
            sys.exit(exception)
        sys.exit(0)

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
    def _print(files: List[str]) -> None:
        tmpdir = file_mod.FileUtil.tmpdir(os.path.join('.cache', 'fprint'))
        pdf = command_mod.Command('pdf', errors='stop')
        xweb = command_mod.Command('xweb', errors='stop')
        task: subtask_mod.Task

        for number, file in enumerate(files):
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" file.',
                )

            tmpfile = f"{tmpdir}/{number:02d}.pdf"
            task = subtask_mod.Batch(pdf.get_cmdline() + [tmpfile, file])
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f"{sys.argv[0]}: Cannot convert to PDF: {file}",
                )

            print(f"Sending to browser for printing: {file}")
            task = subtask_mod.Daemon(xweb.get_cmdline() + [tmpfile])
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
