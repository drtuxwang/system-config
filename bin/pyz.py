#!/usr/bin/env python3
"""
Make a Python 3 ZIP Application in PYZ format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import BinaryIO, List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archive(self) -> str:
        """
        Return archive location.
        """
        return self._args.archive

    def get_archiver(self) -> Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a Python3 ZIP Application in PYZ format.",
        )

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.pyz',
            help="Archive file.",
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File to archive.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._archiver = Command('pkzip32.exe', errors='ignore')
            if self._archiver.is_found():
                self._archiver.set_args([
                    '-add',
                    '-maximum',
                    '-recurse',
                    '-path',
                    self._args.archive[0] + '-zip'
                ])
            else:
                self._archiver = Command(
                    'zip',
                    args=['-r', '-9', self._args.archive[0] + '-zip'],
                    errors='stop'
                )
        else:
            self._archiver = Command(
                'zip',
                args=['-r', '-9', self._args.archive[0] + '-zip'],
                errors='stop'
            )

        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())

        if '__main__.py' not in self._archiver.get_args():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "__main__.py" main program file.',
            )


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

    def _make_pyz(self, path: Path) -> None:
        path_new = Path(f'{path}-zip')
        try:
            with path.open('wb') as ofile:
                ofile.write(b"#!/usr/bin/env python3\n")
                with path_new.open('rb') as ifile:
                    self._copy(ifile, ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create '
                f'"{path}" Python3 ZIP Application.',
            ) from exception
        try:
            path_new.replace(path)
        except OSError:
            pass
        path.chmod(0o755)

    @staticmethod
    def _copy(ifile: BinaryIO, ofile: BinaryIO) -> None:
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        archiver = options.get_archiver()

        task = Task(archiver.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
                file=sys.stderr,
            )
            raise SystemExit(task.get_exitcode())
        self._make_pyz(Path(options.get_archive()))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
