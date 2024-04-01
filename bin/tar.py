#!/usr/bin/env python3
"""
Make optional compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.ZST/TAR.LZMA/
TAR.XZ/TAR.7Z/TGZ/TBZ/TZS/TZST/TLZ/TXZ/T7Z format (GNU Tar version).
"""

import argparse
import getpass
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileStat
from subtask_mod import Batch, Exec, Task


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
        return self._archive

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make optional compressed archive in TAR/TAR.GZ/"
            "TAR.BZ2/TAR.ZSTD/TAR.LZMA/TAR.XZ/TAR.7Z (TGZ/TBZ/TZS|TZST|TLZ/"
            "TXZ|T7Z) format.",
        )

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.tar',
            help="Archive file.",
        )
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
        self._parse_args(args[1:])

        self._archive = (
            f'{Path(self._args.archive[0]).resolve()}.tar'
            if Path(self._args.archive[0]).is_dir()
            else self._args.archive[0]
        )
        self._files = self._args.files if self._args.files else os.listdir()


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

    @classmethod
    def _pack(  # pylint: disable=too-many-branches
        cls,
        archive: str,
        files: List[str],
    ) -> None:
        task: Task

        tar = Command('tar', errors='stop')
        task = Batch(tar.get_cmdline() + ['--help'])
        task.run(pattern='--owner|--numeric-owner|--xattrs')
        cmdline = tar.get_cmdline() + ['cf', '-'] + files
        if getpass.getuser() == 'root':
            if task.is_match_output('--numeric-owner'):
                cmdline.append('--numeric-owner')
            if task.is_match_output('--xattrs'):
                cmdline.extend(['--xattrs', '--xattrs-include=*'])
        elif task.is_match_output('--owner'):
            cmdline.extend(['--owner=0:0', '--group=0:0'])

        path_tmp = Path(f'{archive}.part')
        name = archive.replace('-new', '')
        if name.endswith(('.tar.7z', 't7z')):
            cmdline.extend(['|'] + Command('7z', args=[
                'a',
                '-m0=lzma2',
                '-mmt=2',
                '-mx=9',
                '-myx=9',
                '-md=128m',
                '-mfb=256',
                '-ms=on',
                '-bsp1',
                '-y',
                '-si',
                path_tmp,
            ], errors='stop').get_cmdline())
        else:
            monitor = Command('pv', errors='ignore')
            if monitor.is_found():
                cmdline.extend(['|'] + monitor.get_cmdline())
            if name.endswith(('.tar.xz', '.txz')):
                cmdline.extend(['|'] + Command('xz', args=[
                    '-9',
                    '-e',
                    '--x86',
                    '--lzma2=dict=128MiB',
                    '--threads=1',
                    '--verbose',
                ], errors='stop').get_cmdline())
            elif name.endswith(('.tar.lzma', '.tlz')):
                cmdline.extend(['|'] + Command('xz', args=[
                    '-9',
                    '-e',
                    '--format=lzma',
                    '--threads=1',
                    '--verbose',
                ], errors='stop').get_cmdline())
            elif name.endswith(('.tar.zst', '.tar.zstd', '.tzs', '.tzst')):
                cmdline.extend(['|'] + Command(
                    'zstd',
                    args=['--ultra', '-22', '-T0'],
                    errors='stop',
                ).get_cmdline())
            elif name.endswith(('.tar.bz2', '.tbz')):
                cmdline.extend(['|'] + Command(
                    'bzip2',
                    args=['-9'],
                    errors='stop',
                ).get_cmdline())
            elif name.endswith(('.tar.gz', '.tgz')):
                cmdline.extend(['|'] + Command(
                    'gzip',
                    args=['-9'],
                    errors='stop',
                ).get_cmdline())
            elif name.endswith(('.tar')):
                cmdline.extend(['|'] + Command(
                    'cat',
                    errors='stop',
                ).get_cmdline())
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Unsupported "{archive}" archive format.',
                )
            cmdline.extend(['>', f'{archive}.part'])

        task = Task(cmdline)
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())
        if name.endswith('.tar'):
            cls._check_tar(path_tmp)
        try:
            path_tmp.replace(archive)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{archive}" archive file.',
            ) from exception

    @staticmethod
    def _check_tar(path: Path) -> None:
        size = FileStat(path).get_size()
        if size % 1024:
            raise SystemExit(f'{sys.argv[0]}: Truncated tar file: {path}')

        with path.open('rb') as ifile:
            ifile.seek(size - 1024)
            if ifile.read(1024) != 1024*b'\0':
                raise SystemExit(
                    f'{sys.argv[0]}: Missing tar file EOF records: {path}'
                )

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        if os.name == 'nt':
            tar = Command('tar_py.py', errors='stop')
            Exec(tar.get_cmdline() + sys.argv[1:]).run()

        os.umask(0o022)
        cls._pack(options.get_archive(), options.get_files())
        print("Completed!")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
