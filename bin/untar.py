#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/
TAR.7Z/TGZ/TBZ/TLZ/TXZ format (GNU Tar version).
"""

import argparse
import glob
import os
import re
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
            description='Unpack a compressed archive in TAR/TAR.GZ/TAR.BZ2/'
            'TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.',
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.tar|file.tar.gz|file.tar.bz2|file.tar.lzma|'
            'file.tar.xz|file.tar.7z|file.tgz|file.tbz|file.tlz|file.txz',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

        isarchive = re.compile('[.](tar|tar[.](gz|bz2|lzma|xz|7z)|t[gblx]z)$')
        for archive in self._args.archives:
            if not isarchive.search(archive):
                raise SystemExit(
                    sys.argv[0] + ': Unsupported "' + archive +
                    '" archive format.'
                )

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

    def _unpack(self, file: str) -> None:
        task = subtask_mod.Batch(self._tar.get_cmdline() + ['--help'])
        task.run(pattern='--xattrs')
        has_xattrs = task.has_output()

        if file.endswith('.tar.7z'):
            p7zip = command_mod.Command('7z', errors='stop')
            p7zip.set_args(['x', '-y', '-so', file])
            self._tar.set_args(['xfv', '-'])
            if has_xattrs:
                self._tar.extend_args(['--xattrs', '--xattrs-include=*'])
            subtask_mod.Task(
                p7zip.get_cmdline() + ['|'] + self._tar.get_cmdline()).run()
        else:
            self._tar.set_args(['xfv', file])
            if has_xattrs:
                self._tar.extend_args(['--xattrs', '--xattrs-include=*'])
            subtask_mod.Task(self._tar.get_cmdline()).run()

    def _view(self, file: str) -> None:
        if file.endswith('.tar.7z'):
            p7zip = command_mod.Command('7z', errors='stop')
            p7zip.set_args(['x', '-y', '-so', file])
            self._tar.set_args(['tfv', '-'])
            subtask_mod.Task(
                p7zip.get_cmdline() + ['|'] + self._tar.get_cmdline()).run()
        else:
            self._tar.set_args(['tfv', file])
            subtask_mod.Task(self._tar.get_cmdline()).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        if os.name == 'nt':
            self._tar = command_mod.Command('tar.exe', errors='stop')
        else:
            self._tar = command_mod.Command('tar', errors='stop')

        for file in options.get_archives():
            print(file + ':')
            if options.get_view_flag():
                self._view(file)
            else:
                self._unpack(file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
