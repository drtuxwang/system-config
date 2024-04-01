#!/usr/bin/env python3
"""
Convert image file to text using OCR.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from config_mod import Config
from file_mod import FileUtil
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_convert(self) -> Command:
        """
        Return convert Command class object.
        """
        return self._convert

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_tesseract(self) -> Command:
        """
        Return tesseract Command class object.
        """
        return self._tesseract

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Convert image file to text using OCR.",
        )

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help="Image file to analyse.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = Command('convert', errors='stop')
        self._tesseract = Command('tesseract', errors='stop')
        self._tesseract.set_args(['--psm', '11', '-l', 'eng'])


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

    def _ocr(self, path: Path, name: str) -> None:
        task = Task(self._tesseract.get_cmdline() + [path, name])
        task.run(pattern='^Tesseract')
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._tesseract = options.get_tesseract()
        convert = options.get_convert()

        tmpdir = FileUtil.tmpdir('.cache')
        tmp_path = Path(tmpdir, f'ocr.tmp{os.getpid()}')

        images_extensions = Config().get('image_extensions')

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" image file.',
                )
            ext = path.suffix.lower()
            if ext in images_extensions:
                print(f'Converting "{path}" to "{path.stem}.txt"...')
                task = Task(convert.get_cmdline() + [path, tmp_path])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
                self._ocr(tmp_path, path.stem)
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            elif ext in ('tif', 'tiff'):
                print(f'Converting "{path}" to "{path.stem}.txt"...')
                self._ocr(path, path.stem)
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot OCR non image file "{path}".',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
