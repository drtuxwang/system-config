#!/usr/bin/env python3
"""
Unpack an archive in TAR format (Python version).
"""

import argparse
import glob
import os
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
            description="Unpack an archive in TAR format.",
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
            metavar='file.tar',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        for archive in self._args.archives:
            if not archive.endswith('.tar'):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsupported "{archive}" archive format.',
                )


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
    def _unpack(archive: tarfile.TarFile) -> None:
        for file in archive.getnames():
            print(file)
            if os.path.isabs(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsafe to extract file with absolute '
                    'path outside of current directory.'
                )
            if file.startswith(os.pardir):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsafe to extract file with relative '
                    'path outside of current directory.'
                )
            try:
                archive.extract(archive.getmember(file))
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Unable to create "{file}" extracted.',
                ) from exception
            if not os.path.isfile(file):
                if not os.path.isdir(file):
                    if not os.path.islink(file):
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create extracted '
                            f'"{file}" file.',
                        )

    @staticmethod
    def _view(archive: tarfile.TarFile) -> None:
        archive.list()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        for file in options.get_archives():
            if file.endswith('.tar'):
                print(f"{file}:")
                try:
                    with tarfile.open(file, 'r:') as archive:
                        if options.get_view_flag():
                            cls._view(archive)
                        else:
                            cls._unpack(archive)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot open "{file}" archive file.',
                    ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()