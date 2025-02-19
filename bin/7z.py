#!/usr/bin/env python3
"""
Make a compressed archive in 7Z format.
"""
# pylint: disable=invalid-name

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import BinaryIO, List

from command_mod import Command
from file_mod import FileStat
from subtask_mod import Exec, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archiver(self) -> Command:
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archive(self) -> str:
        """
        Return archive file.
        """
        return self._archive

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a compressed archive in 7z format.",
        )

        parser.add_argument(
            '-split',
            nargs=1,
            type=int,
            metavar='bytes',
            help="Split archive into chucks with selected size.",
        )
        parser.add_argument(
            '-threads',
            nargs=1,
            type=int,
            default=[2],
            help="Threads are faster but decrease quality. Default is 2.",
        )
        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.7z|file.bin|file.exe|directory',
            help="Archive file or directory.",
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File or directory.",
        )

        self._args = parser.parse_args(args)

        if self._args.split and self._args.split[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for split size.',
            )
        if self._args.threads[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer for '
                'number of threads.'
            )

    @staticmethod
    def _setenv() -> None:
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._archiver = Command('7z', errors='stop')

        if len(args) > 1 and args[1] in ('a', '-bd', 'l', 't', 'x'):
            self._archiver.set_args(args[1:])
            Exec(self._archiver.get_cmdline()).run()

        self._parse_args(args[1:])

        threads = str(self._args.threads[0])
        if threads == '1':
            self._archiver.set_args(['a', '-m0=lzma', '-mmt=1'])
        else:
            self._archiver.set_args(['a', '-m0=lzma2', f'-mmt={threads}'])
        self._archiver.extend_args([
            '-mx=9',
            '-myx=9',
            '-md=256m',
            '-mfb=273',
            '-mqs=on',
            '-ms=on',
            '-snh',
            '-snl',
            '-stl',
            '-bsp1',
            '-y',
        ])
        if self._args.split:
            self._archiver.extend_args([f'-v{self._args.split[0]}b'])

        path = Path(self._args.archive[0])
        if path.is_dir():
            self._archive = (
                f'{Path.cwd().with_name(path.resolve().name)}.7z'.lower()
            )
            self._archiver.extend_args([self._archive+'.part', path])
        else:
            self._archive = str(path)
            self._archiver.append_arg(self._archive+'.part')

        if self._args.files:
            self._archiver.extend_args(self._args.files)

        self._setenv()


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
    def _copy(ifile: BinaryIO, ofile: BinaryIO) -> None:
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)

    @classmethod
    def _make_exe(cls, archiver: Command, path: Path) -> None:
        command = Command('7z.sfx', platform='windows-x86', errors='ignore')
        if not command.is_found():
            command = Command(
                '7z.sfx',
                directory=Path(archiver.get_file()).parent,
                platform='windows-x86',
                errors='ignore'
            )
        sfx_path = Path(command.get_file())
        if not sfx_path.is_file():
            archiver = Command(archiver.get_file(), errors='ignore')
            if not archiver.is_found():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{sfx_path}" SFX file.',
                )
            Exec(archiver.get_cmdline() + sys.argv[1:]).run()

        print("Adding SFX code")
        path_new = Path(f'{path}-sfx')
        with path_new.open('wb') as ofile:
            try:
                with sfx_path.open('rb') as ifile:
                    cls._copy(ifile, ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{sfx_path}" SFX file.',
                ) from exception
            with path.open('rb') as ifile:
                cls._copy(ifile, ofile)

        file_time = FileStat(path).get_mtime()
        os.utime(path_new, (file_time, file_time))
        try:
            path_new.chmod(0o755)
            path_new.replace(path)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot rename "{path_new}" file to "{path}".',
            ) from exception

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

        os.umask(0o022)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        archiver = options.get_archiver()
        archive = options.get_archive()

        task = Task(archiver.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
                file=sys.stderr,
            )
            raise SystemExit(task.get_exitcode())

        if archive.endswith('.exe'):
            self._make_exe(archiver, Path(f'{archive}.part'))

        try:
            Path(f'{archive}.part').replace(archive)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{archive}" archive file.',
            ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
