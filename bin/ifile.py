#!/usr/bin/env python3
"""
Determine image file information
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import imagesize  # type: ignore
import magic  # type: ignore

from config_mod import Config
from logging_mod import Message


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
            description="Determine image file information."
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
    _image_extensions = Config().get('image_extensions')

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

    @staticmethod
    def _get_info(file: str) -> str:
        info = magic.from_file(file, mime=True)
        if info.startswith('image/'):
            x, y = imagesize.get(file)
            info = f'{info}  {x}:{y}'
        return info

    @classmethod
    def _show(cls, files: List[str]) -> None:
        files = [x for x in files if Path(x).suffix in cls._image_extensions]
        if files:
            width = max(Message(x).width() for x in files)
            for file in files:
                print(f"{Message(file).get(width)}  {cls._get_info(file)}")

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        files = options.get_files()

        cls._show(files)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
