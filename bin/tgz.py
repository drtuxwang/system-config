#!/usr/bin/env python3
"""
Make a compressed archive in TAR.GZ format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
import tarfile
from typing import List


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
            description="Make a compressed archive in TAR.GZ format.",
        )

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.tar.gz|file.tgz',
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
            self._archive = os.path.abspath(self._args.archive[0]) + '.tar.gz'
        else:
            self._archive = self._args.archive[0]
        if '.tar.gz' not in self._archive and '.tgz' not in self._archive:
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
    def _reset(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = '0'
        return tarinfo

    @classmethod
    def _addfile(cls, ofile: tarfile.TarFile, files: List[str]) -> None:
        for file in sorted(files):
            print(file)
            try:
                ofile.add(file, recursive=False, filter=cls._reset)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot add "{file}" file to archive.',
                ) from exception
            if os.path.isdir(file) and not os.path.islink(file):
                try:
                    cls._addfile(
                        ofile,
                        [os.path.join(file, x) for x in os.listdir(file)]
                    )
                except PermissionError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot open "{file}" directory.',
                    ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        archive = options.get_archive()
        try:
            with tarfile.open(options.get_archive()+'.part', 'w:gz') as ofile:
                self._addfile(ofile, options.get_files())
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{archive}.part" archive file.',
            ) from exception
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
