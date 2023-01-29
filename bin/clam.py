#!/usr/bin/env python3
"""
Run CLAMAV anti-virus scanner.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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

    def get_clamscan(self) -> command_mod.Command:
        """
        Return clamscan Command class object.
        """
        return self._clamscan

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Run ClamAV anti-virus scanner.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File or directory.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._clamscan = command_mod.Command('clamscan', errors='stop')
        self._clamscan.set_args(['-r'] + self._args.files)


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
        clamscan = options.get_clamscan()

        task = subtask_mod.Task(clamscan.get_cmdline())
        task.run()
        print("---------- VIRUS DATABASE ----------")
        if os.name == 'nt':
            os.chdir(Path(task.get_file()).parent)
            directory_path = Path('database')
        elif Path('/var/clamav').is_dir():
            directory_path = Path('/var/clamav')
        else:
            directory_path = Path('/var/lib/clamav')
        for path in sorted(directory_path.glob('*c[lv]d')):
            file_stat = file_mod.FileStat(path)
            print(
                f"{file_stat.get_size():10d} "
                f"[{file_stat.get_time_local()}] "
                f"{path}",
            )

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
