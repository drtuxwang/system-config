#!/usr/bin/env python3
"""
Make a compressed archive in TAR.LZMA format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
from typing import List

import command_mod
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

    def get_tar(self) -> command_mod.Command:
        """
        Return tar Command class object.
        """
        return self._tar

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a compressed archive in TAR.LZMA format.",
        )

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.tar.lzma|file.tlz',
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
            self._archive = (
                os.path.abspath(self._args.archive[0]) + '.tar.lzma'
            )
        else:
            self._archive = self._args.archive[0]
        if not self._archive.endswith(('.tar.lzma', '.tlz')):
            raise SystemExit(
                f'{sys.argv[0]}: Unsupported "{self._archive}" archive format.'
            )

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()

        self._tar = command_mod.Command('tar', errors='stop')
        self._tar.set_args(['cfv', self._archive+'.part'] + self._files)
        self._tar.extend_args([
            '--use-compress-program',
            'xz -9 -e --format=lzma --threads=1 --verbose',
            '--owner=0:0',
            '--group=0:0',
            '--sort=name',
        ])


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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        archive = options.get_archive()

        os.umask(int('022', 8))

        task = subtask_mod.Task(options.get_tar().get_cmdline())
        task.run()
        try:
            if task.get_exitcode():
                raise OSError
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
