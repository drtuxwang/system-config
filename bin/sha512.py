#!/usr/bin/env python3
"""
Calculate SHA512 checksums of files.
"""

import argparse
import glob
import hashlib
import os
import signal
import sys
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
            description='Calculate MD5 checksums of files.',
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help='Check checksums against files.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|file.sha512sum',
            help='File to checksum or ".sha512sum" checksum file.'
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

    def _calc(self, options: Options, files: List[str]) -> None:
        for file in files:
            if os.path.isdir(file):
                if not os.path.islink(file) and options.get_recursive_flag():
                    try:
                        self._calc(options, sorted(
                            [os.path.join(file, x) for x in os.listdir(file)]))
                    except PermissionError as exception:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot open "' +
                            file + '" directory.'
                        ) from exception
            elif os.path.isfile(file):
                sha512sum = self._sha512sum(file)
                if not sha512sum:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" file.')
                print(sha512sum, file, sep='  ')

    def _check(self, files: List[str]) -> None:
        found = []
        nfiles = 0
        nfail = 0
        nmiss = 0
        for sha512file in files:
            if not os.path.isfile(sha512file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + sha512file +
                    '" sha512sum file.'
                )
            try:
                with open(sha512file, errors='replace') as ifile:
                    for line in ifile:
                        sha512sum = line[:32]
                        file = line.rstrip()[34:]
                        if len(sha512sum) == 32 and file:
                            found.append(file)
                            nfiles += 1
                            test = self._sha512sum(file)
                            if not test:
                                print(file, '# FAILED open or read')
                                nmiss += 1
                            elif test != sha512sum:
                                print(file, '# FAILED checksum')
                                nfail += 1
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + sha512file +
                    '" sha512sum file.'
                ) from exception
        if nmiss > 0:
            print("sha512: Cannot find", nmiss, "of", nfiles, "listed files.")
        if nfail > 0:
            print(
                "sha512: Mismatch in", nfail, "of", nfiles - nmiss,
                "computed checksums."
            )

    @staticmethod
    def _sha512sum(file: str) -> str:
        try:
            with open(file, 'rb') as ifile:
                sha512 = hashlib.sha512()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    sha512.update(chunk)
        except (OSError, TypeError) as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.'
            ) from exception
        return sha512.hexdigest()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._calc(options, options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
