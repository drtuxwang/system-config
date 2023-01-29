#!/usr/bin/env python3
"""
Calculate PAR2 parity and repair tool.
"""

import argparse
import logging
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import logging_mod
import subtask_mod

IGNORE_SUFFIXES = ('.fsum', '.md5', '.md5sum', '.par2')

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of file.
        """
        return self._args.files

    def get_par2(self) -> command_mod.Command:
        """
        Return par2 Command class object.
        """
        return self._par2

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Parity and repair tool.")

        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File or directory.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._par2 = command_mod.Command('par2', errors='stop')
        self._par2.set_args(['c', '-q', '-n1', '-r1'])

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
    def _create_3dot_directory(path: Path) -> None:
        if not path.is_dir():
            try:
                path.mkdir()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path}" directory.',
                ) from exception

    @staticmethod
    def _delete_file(path: Path) -> None:
        try:
            path.unlink()
        except OSError:
            pass

    @classmethod
    def _check_3dot_directory(cls, directory_path: Path) -> None:
        if directory_path.is_dir():
            paths = sorted([Path(x.name) for x in directory_path.iterdir()])
            for par_path in paths:
                if par_path.suffix == '.par2':
                    path = Path(directory_path, os.pardir, str(par_path)[:-5])
                    if path.is_file():
                        continue
                    path = Path(directory_path, par_path)
                    logger.warning("Deleting old: %s", path)
                    cls._delete_file(path)
            if not paths:
                os.removedirs(directory_path)

    @classmethod
    def _update(cls, cmdline: List[str], paths: List[Path]) -> None:
        for path in sorted(paths):
            if path.name == '...':
                continue
            directory_path = path.parent
            name = path.name
            if not directory_path:
                directory_path = Path(os.curdir)
            if path.is_dir():
                cls._check_3dot_directory(Path(path, '...'))
                cls._update(cmdline, list(path.glob('*')))
            elif (
                path.is_file() and
                not path.is_symlink() and
                path.stat().st_size
            ):
                suffix = path.suffix
                if len(path.name) == 1 or suffix in IGNORE_SUFFIXES:
                    continue

                fpar_path = Path(directory_path, '...')
                file_time = int(path.stat().st_mtime)
                par_path = Path(directory_path, '...', f'{name}.par2')
                if (
                    not par_path.is_file() or
                    file_time != int(par_path.stat().st_mtime)
                ):
                    tmp_path = Path(directory_path, '....par2')
                    size = path.stat().st_size // 400 * 4 + 4
                    task = subtask_mod.Task(
                        cmdline + ['-s'+str(size), str(tmp_path), str(path)]
                    )
                    cls._create_3dot_directory(fpar_path)
                    task.run(pattern='^$', replace=(
                        'Opening: ',
                        f'Opening: {directory_path}/',
                    ))
                    if task.get_exitcode() == 0:
                        cls._delete_file(tmp_path)
                        try:
                            Path(directory_path, '....vol0+1.par2').replace(
                                par_path
                            )
                            os.utime(par_path, (file_time, file_time))
                        except OSError:
                            pass

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        cmdline = options.get_par2().get_cmdline()
        cls._update(cmdline, [Path(x) for x in options.get_files()])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
