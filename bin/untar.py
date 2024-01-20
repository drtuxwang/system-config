#!/usr/bin/env python3
"""
Unpack optional compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.ZST/TAR.LZMA/
TAR.XZ/TAR.7Z/TGZ/TBZ/TZS/TZST/TLZ/TXZ/T7Z format (GNU Tar version).
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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

    def get_archives(self) -> List[str]:
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack optional compressed archive in TAR/TAR.GZ/"
            "TAR.BZ2/TAR.ZSTD/TAR.LZMA/TAR.XZ/TAR.7Z (TGZ/TBZ/TZS|TZST|TLZ/"
            "TXZ|T7Z) format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='archive',
            help="Archive file.",
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

        os.umask(0o022)

    def _unpack(self, file: str) -> None:
        task: subtask_mod.Task

        if file.endswith(('.tar.7z', '.t7z')):
            unpacker = command_mod.Command('7z', args=['x', '-so'])
        elif file.endswith(('.tar.xz', '.txz')):
            unpacker = command_mod.Command('xz', args=['-d', '-c'])
        elif file.endswith(('.tar.lzma', '.tlz')):
            unpacker = command_mod.Command('lzma', args=['-d', '-c'])
        elif file.endswith(('.tar.zst', '.tar.zstd', '.tzs', '.tzst')):
            unpacker = command_mod.Command('zstd', args=['-d', '-c'])
        elif file.endswith(('.tar.bz2', '.tbz')):
            unpacker = command_mod.Command('bzip2', args=['-d', '-c'])
        elif file.endswith(('.tar.gz', '.tgz')):
            unpacker = command_mod.Command('gzip', args=['-d', '-c'])
        elif file.endswith(('.tar')):
            unpacker = command_mod.Command('cat')
        else:
            raise SystemExit(
                f'{sys.argv[0]}: Unsupported "{file}" archive format.',
            )
        cmdline = unpacker.get_cmdline() + [file]

        monitor = command_mod.Command('pv', errors='ignore')
        if monitor.is_found():
            cmdline.extend(['|'] + monitor.get_cmdline())

        cmdline.extend(['|'] + self._tar.get_cmdline() + ['xf', '-'])
        task = subtask_mod.Batch(self._tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        if task.has_output():
            cmdline.extend(['--xattrs', '--xattrs-include=*'])

        task = subtask_mod.Task(cmdline)
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())

    def _view(self, file: str) -> None:
        if file.endswith('.tar.7z'):
            unpacker = command_mod.Command('7z', errors='stop')
            unpacker.set_args(['x', '-so', file])
            self._tar.set_args(['tfv', '-'])
            subtask_mod.Task(
                unpacker.get_cmdline() + ['|'] + self._tar.get_cmdline()).run()
        else:
            self._tar.set_args(['tfv', file])
            subtask_mod.Task(self._tar.get_cmdline()).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if os.name == 'nt':
            untar = command_mod.Command('untar_py.py', errors='stop')
            subtask_mod.Exec(untar.get_cmdline() + sys.argv[1:]).run()

        self._tar = command_mod.Command('tar', errors='stop')

        for file in options.get_archives():
            print(f"{file}:")
            if options.get_view_flag():
                self._view(file)
            else:
                self._unpack(file)
        print("Completed!")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
