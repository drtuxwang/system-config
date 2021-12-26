#!/usr/bin/env python3
"""
Make a compressed archive in TAR format (GNU Tar version).
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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        task: subtask_mod.Task

        os.umask(int('022', 8))
        archive = options.get_archive()
        if os.name == 'nt':
            tar = command_mod.Command('tar.exe', errors='stop')
        else:
            tar = command_mod.Command('tar', errors='stop')
        task = subtask_mod.Batch(tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        has_xattrs = task.has_output()

        tar.set_args(['cfv', archive+'.part'])
        tar.extend_args(options.get_files())
        if has_xattrs:
            tar.extend_args(['--xattrs', '--xattrs-include=*'])
        task = subtask_mod.Task(tar.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())
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
