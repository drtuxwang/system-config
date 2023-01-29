#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.GZ format.
"""

import argparse
import os
import signal
import sys
import tarfile
from pathlib import Path
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
            description="Unpack a compressed archive in TAR.GZ format.",
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
            metavar='file.tar.gz|file.tgz',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

        for path in [Path(x) for x in self._args.archives]:
            if not path.name.endswith(('.tar.gz', '.tgz')):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsupported "{path}" archive format.',
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

    @staticmethod
    def _unpack(archive: tarfile.TarFile) -> None:
        for path in [Path(x) for x in archive.getnames()]:
            print(path)
            if path.is_absolute():
                raise SystemExit(
                    f'{sys.argv[0]}: Unsafe to extract file with absolute '
                    'path outside of current directory.'
                )
            if str(path).startswith(os.pardir):
                raise SystemExit(
                    f'{sys.argv[0]}: Unsafe to extract file with relative '
                    'path outside of current directory.'
                )
            try:
                archive.extract(archive.getmember(str(path)))
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Unable to create "{path}" extracted.',
                ) from exception
            if not path.exists():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create extracted "{path}" file.',
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

        for file in options.get_archives():
            print(f"{file}:")
            try:
                with tarfile.open(file, 'r:gz') as archive:
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
