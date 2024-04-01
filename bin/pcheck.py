#!/usr/bin/env python3
"""
Check JPEG picture files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Check JPEG picture files.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing JPEG files to check.",
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
        directories = options.get_directories()

        errors = []
        jpeginfo = Command('jpeginfo', errors='stop')
        jpeginfo.set_args(['--info', '--check'])
        for directory_path in [Path(x) for x in directories]:
            if directory_path.is_dir():
                paths = []
                for path in Path(directory_path).glob('*.*'):
                    if path.suffix.lower() in ('.jpg', '.jpeg'):
                        paths.append(path)
                if paths:
                    task = Batch(jpeginfo.get_cmdline() + paths)
                    task.run()
                    for line in task.get_output():
                        if '[ERROR]' in line:
                            errors.append(line)
                        else:
                            print(line)
        if errors:
            for line in errors:
                print(line)
            raise SystemExit(f"Total errors encountered: {len(errors)}.")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
