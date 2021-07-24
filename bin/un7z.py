#!/usr/bin/env python3
"""
Unpack a compressed archive in 7Z format.
"""

import argparse
import glob
import os
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

    def get_archiver(self) -> command_mod.Command:
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
            description='Unpack a compressed archive in 7Z format.',
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            '-test',
            dest='test_flag',
            action='store_true',
            help='Test archive data only.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.7z',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._archiver = command_mod.Command('7z', errors='stop')

        if self._args.view_flag:
            self._archiver.set_args(['l'])
        elif self._args.test_flag:
            self._archiver.set_args(['t'])
        else:
            self._archiver.set_args(['x', '-y'])

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
    def set_time(files: List[str]) -> None:
        """
        Fix directory and symbolic link modified times
        """
        for file in files:
            if os.path.islink(file):
                link_stat = file_mod.FileStat(file, follow_symlinks=False)
                file_stat = file_mod.FileStat(file)
                file_time = file_stat.get_time()
                if file_time != link_stat.get_time():
                    try:
                        os.utime(
                            file,
                            (file_time, file_time),
                            follow_symlinks=False,
                        )
                    except NotImplementedError:
                        pass

            elif os.path.isdir(file):
                newest = file_mod.FileUtil.newest(
                    [os.path.join(file, x) for x in os.listdir(file)]
                )
                if not newest:
                    newest = os.path.basename(file)
                file_stat = file_mod.FileStat(newest)
                file_time = file_stat.get_time()
                if file_time != file_mod.FileStat(file).get_time():
                    os.utime(file, (file_time, file_time))

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        archiver = options.get_archiver()

        if os.name == 'nt':
            for archive in options.get_archives():
                task = subtask_mod.Task(archiver.get_cmdline() + [archive])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )
        else:
            for archive in options.get_archives():
                task = subtask_mod.Task(archiver.get_cmdline() + [archive])
                task.run(replace=('\\', '/'))
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )

        archiver.set_args(['l'])
        task = subtask_mod.Batch(archiver.get_cmdline() + [archive])
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
