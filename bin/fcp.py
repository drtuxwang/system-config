#!/usr/bin/env python3
"""
Copy files and directories.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
import time
from typing import List

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_sources(self) -> List[str]:
        """
        Return list of source files.
        """
        return self._args.sources

    def get_target(self) -> str:
        """
        Return target file or directory.
        """
        return self._args.target[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Copy files and directories.',
        )

        parser.add_argument(
            'sources',
            nargs='+',
            metavar='source',
            help='Source file or directory.'
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='target',
            help='Target file or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
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
    def _automount(directory: str, wait: int) -> None:
        if directory.startswith('/media/'):
            for _ in range(0, wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    @staticmethod
    def _copy_link(source: str, target: str) -> None:
        print('Creating "' + target + '" link...')
        source_link = os.readlink(source)

        if os.path.islink(target):
            target_link = os.readlink(target)
            if target_link == source_link:
                return
        elif os.path.isfile(target):
            try:
                os.remove(target)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' + target + '" link.'
                ) from exception

        try:
            os.symlink(source_link, target)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + target + '" link.'
            ) from exception
        file_stat = file_mod.FileStat(source, follow_symlinks=False)
        file_time = file_stat.get_time()
        try:
            os.utime(target, (file_time, file_time), follow_symlinks=False)
        except NotImplementedError:
            pass

    def _copy_directory(self, source: str, target: str) -> None:
        print('Creating "' + target + '" directory...')
        try:
            files = sorted(
                [os.path.join(source, x) for x in os.listdir(source)]
            )
        except PermissionError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + source + '" directory.'
            ) from exception
        if not os.path.isdir(target):
            try:
                os.makedirs(target)
                os.chmod(target, file_mod.FileStat(source).get_mode())
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + target +
                    '" directory.'
                ) from exception
        for file in files:
            self._copy(file, os.path.join(target, os.path.basename(file)))
        newest = file_mod.FileUtil.newest(
            [os.path.join(target, x) for x in os.listdir(target)]
        )
        if not newest:
            newest = source
        file_stat = file_mod.FileStat(newest, follow_symlinks=False)
        file_time = file_stat.get_time()
        os.utime(target, (file_time, file_time))

    @staticmethod
    def _copy_file(source: str, target: str) -> None:
        print('Creating "' + target + '" file...')
        try:
            shutil.copy2(source, target)
        except shutil.Error as exception:
            if 'are the same file' in exception.args[0]:
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy to same "' +
                    target + '" file.'
                ) from exception
            raise SystemExit(
                sys.argv[0] + ': Cannot copy to "' + target + '" file.'
            ) from exception
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with open(source, 'rb'):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            target + '" file.'
                        ) from exception
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + target + '" file.'
                    ) from exception

    def _copy(self, source: str, target: str) -> None:
        if os.path.islink(source):
            self._copy_link(source, target)
        elif os.path.isdir(source):
            self._copy_directory(source, target)
        elif os.path.isfile(source):
            self._copy_file(source, target)

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        sources = self._options.get_sources()
        target = self._options.get_target()
        self._automount(target, 8)

        if len(sources) == 1:
            if not os.path.isdir(target):
                self._copy_file(sources[0], target)
                return 0
        elif not os.path.isdir(target):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + target +
                '" target directory.'
            )

        for source in sources:
            if os.path.isdir(source):
                if (os.path.isabs(source) or
                        source.split(os.sep)[0] in (os.curdir, os.pardir)):
                    targetdir = target
                    self._copy(
                        source,
                        os.path.join(target, os.path.basename(source))
                    )
                else:
                    targetdir = os.path.dirname(os.path.join(target, source))
                    if not os.path.isdir(targetdir):
                        try:
                            os.makedirs(targetdir)
                            os.chmod(
                                targetdir,
                                file_mod.FileStat(source).get_mode()
                            )
                        except OSError as exception:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' +
                                targetdir + '" directory.'
                            ) from exception
                    self._copy(source, os.path.join(target, source))
            else:
                directory = os.path.join(target, os.path.dirname(source))
                if not os.path.isdir(directory):
                    try:
                        os.makedirs(directory)
                    except OSError as exception:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + directory +
                            '" directory.'
                        ) from exception
                self._copy(source, os.path.join(target, source))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
