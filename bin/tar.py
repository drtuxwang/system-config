#!/usr/bin/env python3
"""
Make uncompressed archive in TAR format (GNU Tar version).
"""

import argparse
import glob
import os
import shutil
import signal
import sys
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
            description="Make a compressed archive in TAR format.",
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

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.tar'
        else:
            self._archive = self._args.archive[0]
        if '.tar' not in self._archive:
            raise SystemExit(
                f'{sys.argv[0]}: Unsupported "{self._archive}" archive format.'
            )

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


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
            sys.exit(exception)

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
    def _get_cmdline(archive: str, files: List[str]) -> List[str]:
        if os.name == 'nt':
            tar = command_mod.Command('tar.exe', errors='stop')
        else:
            tar = command_mod.Command('tar', errors='stop')
        task = subtask_mod.Batch(tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        has_xattrs = task.has_output()
        monitor = command_mod.Command('pv', errors='ignore')

        cmdline = tar.get_cmdline()
        if monitor.is_found():
            cmdline.extend(['cf', '-'] + files)
            monitor.set_args(['>', archive+'.part'])
        else:
            cmdline.extend(['cfv', archive+'.part'] + files)
        if has_xattrs:
            cmdline.extend(['--xattrs', '--xattrs-include=*'])
        if monitor.is_found():
            cmdline.extend(['|'] + monitor.get_cmdline())

        return cmdline

    @staticmethod
    def _check_tar(archive: str) -> None:
        size = file_mod.FileStat(archive).get_size()
        if size % 1024:
            raise SystemExit(f'{sys.argv[0]}: Truncated tar file: {archive}')

        with open(archive, 'rb') as ifile:
            ifile.seek(size - 1024)
            if ifile.read(1024) != 1024*b'\0':
                raise SystemExit(
                    f'{sys.argv[0]}: Missing tar file EOF records: {archive}'
                )

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        task: subtask_mod.Task

        os.umask(int('022', 8))
        archive = options.get_archive()
        task = subtask_mod.Task(cls._get_cmdline(archive, options.get_files()))
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())
        cls._check_tar(archive + '.part')
        try:
            shutil.move(archive+'.part', archive)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{archive}" archive file.',
            ) from exception
        print("Completed!")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
