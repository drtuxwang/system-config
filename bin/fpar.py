#!/usr/bin/env python3
"""
Calculate PAR2 parity and repair tool.
"""

import argparse
import glob
import logging
import os
import shutil
import signal
import sys
from typing import List

import command_mod
import logging_mod
import subtask_mod

IGNORE_EXTENSIONS = ('.fsum', '.md5', '.md5sum', '.par2')

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
    def _create_3dot_directory(directory: str) -> None:
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{directory}" directory.',
                ) from exception

    @staticmethod
    def _delete_file(file: str) -> None:
        try:
            os.remove(file)
        except OSError:
            pass

    @classmethod
    def _check_3dot_directory(cls, directory: str) -> None:
        if os.path.isdir(directory):
            for par_file in sorted(os.listdir(directory)):
                if par_file.endswith('.par2'):
                    file = os.path.join(directory, os.pardir, par_file[:-5])
                    if os.path.isfile(file):
                        continue
                    file = os.path.join(directory, par_file)
                    logger.warning("Deleting old: %s", file)
                    cls._delete_file(file)
            if not os.listdir(directory):
                os.removedirs(directory)

    @classmethod
    def _update(cls, cmdline: List[str], files: List[str]) -> None:
        for file in sorted(files):
            directory, name = os.path.split(file)
            if not directory:
                directory = os.curdir
            if os.path.isdir(file):
                cls._check_3dot_directory(os.path.join(file, '...'))
                cls._update(cmdline, glob.glob(os.path.join(file, '*')))
            elif (
                os.path.isfile(file) and
                not os.path.islink(file) and
                os.path.getsize(file)
            ):
                fpar_directory = os.path.join(directory, '...')

                if name.endswith(IGNORE_EXTENSIONS):
                    continue

                file_time = os.path.getmtime(file)
                par_file = os.path.join(directory, '...', name+'.par2')
                if (
                        not os.path.isfile(par_file) or
                        file_time != os.path.getmtime(par_file)
                ):
                    tmpfile = os.path.join(directory, '....par2')
                    size = os.path.getsize(file) // 400 * 4 + 4
                    task = subtask_mod.Task(
                        cmdline + ['-s'+str(size), tmpfile, file]
                    )
                    cls._create_3dot_directory(fpar_directory)
                    task.run(pattern='^$', replace=(
                        'Opening: ',
                        f'Opening: {directory}{os.sep}',
                    ))
                    if task.get_exitcode() == 0:
                        cls._delete_file(tmpfile)
                        try:
                            shutil.move(
                                os.path.join(directory, '....vol0+1.par2'),
                                par_file
                            )
                            os.utime(par_file, (file_time, file_time))
                        except OSError:
                            pass

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        cmdline = options.get_par2().get_cmdline()
        cls._update(cmdline, options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
