#!/usr/bin/env python3
"""
Show full list of files.
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import Iterator, List, Union

import command_mod
import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._files

    def get_order(self) -> str:
        """
        Return display order.
        """
        return self._args.order

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_reverse_flag(self) -> bool:
        """
        Return reverse flag.
        """
        return self._args.reverse_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Show full list of files.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Show directories recursively.",
        )
        parser.add_argument(
            '-s',
            action='store_const',
            const='size',
            dest='order',
            default='name',
            help="Sort files by size.",
        )
        parser.add_argument(
            '-t',
            action='store_const',
            const='mtime',
            dest='order',
            default='name',
            help="Sort files by modification time.",
        )
        parser.add_argument(
            '-c',
            action='store_const',
            const='ctime',
            dest='order',
            default='name',
            help="Sort files by meta data change time."
        )
        parser.add_argument(
            '-v',
            action='store_const',
            const='version',
            dest='order',
            default='name',
            help="Sort files as loose versions."
        )
        parser.add_argument(
            '-r',
            dest='reverse_flag',
            action='store_true',
            help="Reverse order."
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File or directory."
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = sorted(os.listdir())


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

    def _list(self, options: Options, files: List[str]) -> None:
        file_stats = []
        for path in [Path(x) for x in files]:
            if path.is_symlink():
                file_stats.append(file_mod.FileStat(path, size=0))
            elif path.is_dir():
                file_stats.append(file_mod.FileStat(f'{path}/'))
            elif path.is_file():
                file_stats.append(file_mod.FileStat(path))
        for file_stat in self._sorted(options, file_stats):
            print(
                f"{file_stat.get_size():10d} "
                f"[{file_stat.get_time_local()}] "
                f"{file_stat.get_file()}",
            )
            if (
                options.get_recursive_flag() and
                file_stat.get_file().endswith(os.sep)
            ):
                self._list(options, sorted(
                    glob.glob(file_stat.get_file() + '.*') +
                    glob.glob(file_stat.get_file() + '*')
                ))

    @staticmethod
    def _sorted(
        options: Options,
        file_stats: List[file_mod.FileStat],
    ) -> Union[Iterator[file_mod.FileStat], List[file_mod.FileStat]]:
        order = options.get_order()
        if order == 'ctime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time_change())
        elif order == 'mtime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time())
        elif order == 'size':
            file_stats = sorted(file_stats, key=lambda s: s.get_size())
        elif order == 'version':
            file_stats = sorted(
                file_stats,
                key=lambda s: command_mod.LooseVersion(s.get_file()),
            )
        if options.get_reverse_flag():
            return reversed(file_stats)
        return file_stats

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._list(options, options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
