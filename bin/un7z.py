#!/usr/bin/env python3
"""
Unpack a compressed archive in 7Z format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileStat, FileUtil
from subtask_mod import Batch, Task


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

    def get_archives(self) -> List[str]:
        """
        Return list of archive files.
        """
        return self._args.archives

    @staticmethod
    def _setenv() -> None:
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in 7Z format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            '-test',
            dest='test_flag',
            action='store_true',
            help="Test archive data only.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.7z',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._archiver = Command('7zz', errors='ignore')
        if not self._archiver.is_found():
            self._archiver = Command('7z', errors='stop')

        if self._args.view_flag:
            self._archiver.set_args(['l'])
        elif self._args.test_flag:
            self._archiver.set_args(['t'])
        else:
            self._archiver.set_args(['x', '-y', '-snld'])

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
    def set_time(files: List[str]) -> None:
        """
        Fix directory and symbolic link modified times
        """
        for path in [Path(x) for x in files]:
            if path.is_symlink():
                link_stat = FileStat(path, follow_symlinks=False)
                file_stat = FileStat(path)
                file_time = file_stat.get_time()
                if file_time != link_stat.get_time():
                    try:
                        os.utime(
                            path,
                            (file_time, file_time),
                            follow_symlinks=False,
                        )
                    except NotImplementedError:
                        pass

            elif path.is_dir():
                newest = FileUtil.newest(list(path.iterdir()))
                if not newest:
                    newest = path.name
                file_stat = FileStat(newest)
                file_time = file_stat.get_time()
                if file_time != FileStat(path).get_time():
                    os.utime(path, (file_time, file_time))

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(0o022)
        archiver = options.get_archiver()

        if os.name == 'nt':
            for archive in options.get_archives():
                task = Task(archiver.get_cmdline() + [archive])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
        else:
            for archive in options.get_archives():
                task = Task(archiver.get_cmdline() + [archive])
                task.run(replace=('\\', '/'))
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )

        archiver.set_args(['l'])
        task = Batch(archiver.get_cmdline() + [archive])
        task.run(pattern=r"\d\d:\d\d:\d\d (D....|....A) ")
        files = [line[53:] for line in task.get_output()]
        files.reverse()
        cls.set_time(files)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
