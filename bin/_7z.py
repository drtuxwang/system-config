#!/usr/bin/env python3
"""
Make a compressed archive in 7Z format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
from typing import BinaryIO, List

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

    def get_archiver(self) -> command_mod.Command:
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
        for name in ('7zzs', '7zz'):
            self._archiver = command_mod.Command(name, errors='ignore')
            if self._archiver.is_found():
                break
        else:
            self._archiver = command_mod.Command('7z', errors='stop')

        if len(args) > 1 and args[1] in ('a', '-bd', 'l', 't', 'x'):
            self._archiver.set_args(args[1:])
            subtask_mod.Exec(self._archiver.get_cmdline()).run()

        self._parse_args(args[1:])

        threads = str(self._args.threads[0])
        if threads == '1':
            self._archiver.set_args(['a', '-m0=lzma', '-mmt=1'])
        else:
            self._archiver.set_args(['a', '-m0=lzma2', f'-mmt={threads}'])
        self._archiver.extend_args([
            '-mx=9',
            '-myx=9',
            '-md=128m',
            '-mfb=256',
            '-ms=on',
            '-snh',
            '-snl',
            '-stl',
            '-y',
        ])
        if self._args.split:
            self._archiver.extend_args([f'-v{self._args.split[0]}b'])

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.7z'
        else:
            self._archive = self._args.archive[0]
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
    def _make_exe(cls, archiver: command_mod.Command, archive: str) -> None:
        command = command_mod.Command(
            '7z.sfx',
            platform='windows-x86',
            errors='ignore'
        )
        if not command.is_found():
            command = command_mod.Command(
                '7z.sfx',
                directory=os.path.dirname(archiver.get_file()),
                platform='windows-x86',
                errors='ignore'
            )
        sfx = command.get_file()
        if not os.path.isfile(sfx):
            archiver = command_mod.Command(
                archiver.get_file(), args=sys.argv[1:], errors='ignore')
            if not archiver.is_found():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{sfx}" SFX file.',
                )
            subtask_mod.Exec(archiver.get_cmdline()).run()

        print("Adding SFX code")
        archive_sfx = archive + '-sfx'
        with open(archive_sfx, 'wb') as ofile:
            try:
                with open(sfx, 'rb') as ifile:
                    cls._copy(ifile, ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{sfx}" SFX file.',
                ) from exception
            with open(archive, 'rb') as ifile:
                cls._copy(ifile, ofile)

        file_stat = file_mod.FileStat(archive)
        os.utime(archive_sfx, (file_stat.get_time(), file_stat.get_time()))
        try:
            os.chmod(archive_sfx, int('755', 8))
            shutil.move(archive_sfx, archive)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot rename '
                f'"{archive_sfx}" file to "{archive}".',
            ) from exception

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

    def run(self) -> int:
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()
        archiver = options.get_archiver()
        archive = options.get_archive()

        task = subtask_mod.Task(archiver.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
                file=sys.stderr,
            )
            raise SystemExit(task.get_exitcode())

        if archive.endswith('.exe'):
            self._make_exe(archiver, archive+'.part')

        try:
            shutil.move(archive+'.part', archive)
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
