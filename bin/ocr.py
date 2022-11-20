#!/usr/bin/env python3
"""
Convert image file to text using OCR.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import config_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_convert(self) -> command_mod.Command:
        """
        Return convert Command class object.
        """
        return self._convert

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_tesseract(self) -> command_mod.Command:
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

        self._convert = command_mod.Command('convert', errors='stop')
        self._tesseract = command_mod.Command('tesseract', errors='stop')
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _ocr(self, file: str, name: str) -> None:
        task = subtask_mod.Task(self._tesseract.get_cmdline() + [file, name])
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

        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        tmpfile = os.path.join(tmpdir, f'ocr.tmp{os.getpid()}')

        images_extensions = config_mod.Config().get('image_extensions')

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" image file.',
                )
            root, ext = os.path.splitext(file.lower())
            if ext in images_extensions:
                print(f'Converting "{file}" to "{root}.txt"...')
                task = subtask_mod.Task(
                    convert.get_cmdline() + [file, tmpfile])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
                self._ocr(tmpfile, root)
                try:
                    os.remove(tmpfile)
                except OSError:
                    pass
            elif ext in ('tif', 'tiff'):
                print(f'Converting "{file}" to "{root}.txt"...')
                self._ocr(file, root)
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot OCR non image file "{file}".',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
