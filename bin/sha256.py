#!/usr/bin/env python3
"""
Calculate SHA256 checksums of files.
"""

import argparse
import hashlib
import os
import signal
import sys
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_check_flag(self) -> bool:
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Calculate MD5 checksums of files.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help="Check checksums against files.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|file.sha256sum',
            help='File to checksum or ".sha256sum" checksum file.',
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

    def _calc(self, options: Options, paths: List[Path]) -> None:
        for path in paths:
            if path.is_dir():
                if not path.is_symlink() and options.get_recursive_flag():
                    try:
                        self._calc(options, sorted(path.iterdir()))
                    except PermissionError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot open "{path}" directory.',
                        ) from exception
            elif path.is_file():
                sha256sum = self._sha256sum(path)
                if not sha256sum:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{path}" file.',
                    )
                print(sha256sum, path, sep='  ')

    def _check(self, files: List[str]) -> None:
        found = []
        nfiles = 0
        nfail = 0
        nmiss = 0
        for path in [Path(x) for x in files]:
            if not path.is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" sha256sum file.',
                )
            try:
                with path.open(errors='replace') as ifile:
                    for line in ifile:
                        sha256sum = line[:32]
                        file = line.rstrip()[34:]
                        if len(sha256sum) == 32 and file:
                            found.append(file)
                            nfiles += 1
                            test = self._sha256sum(Path(file))
                            if not test:
                                print(file, '# FAILED open or read')
                                nmiss += 1
                            elif test != sha256sum:
                                print(file, '# FAILED checksum')
                                nfail += 1
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{path}" sha256sum file.',
                ) from exception
        if nmiss > 0:
            print("sha256: Cannot find", nmiss, "of", nfiles, "listed files.")
        if nfail > 0:
            print(
                "sha256: Mismatch in", nfail, "of", nfiles - nmiss,
                "computed checksums."
            )

    @staticmethod
    def _sha256sum(path: Path) -> str:
        try:
            with path.open('rb') as ifile:
                sha256 = hashlib.sha256()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    sha256.update(chunk)
        except (OSError, TypeError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.',
            ) from exception
        return sha256.hexdigest()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._calc(options, [Path(x) for x in options.get_files()])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
