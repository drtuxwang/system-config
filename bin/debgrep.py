#!/usr/bin/env python3
"""
Search Debian package json.zstd file.
"""

import argparse
import json
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

import pyzstd


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_full(self) -> bool:
        """
        Return full info flag.
        """
        return self._args.full

    def get_pattern(self) -> str:
        """
        Return regular expression search pattern.
        """
        return self._args.pattern[0]

    def get_packages_file(self) -> List[str]:
        """
        Return packages file location.
        """
        return self._args.packages_files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Print lines matching a pattern in Debian "
            "package files.",
        )

        parser.add_argument(
            '-a',
            dest='full',
            action='store_true',
            help="Show full info about matched packages.",
        )
        parser.add_argument(
            'pattern',
            nargs=1,
            metavar='pattern',
            help="Regular expression.",
        )
        parser.add_argument(
            'packages_files',
            nargs='+',
            metavar='distro.json.zstd',
            help="Debian package file.",
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
            self._packages: dict = {}
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
    def _read_data(path: Path) -> dict:
        try:
            data = json.loads(pyzstd.decompress(  # pylint: disable=no-member
                 path.read_bytes()
            ))
        except json.decoder.JSONDecodeError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Corrupt "{path}" file.',
            ) from exception
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.'
            ) from exception

        return data

    @classmethod
    def _grep(cls, message: str, pattern: str, path: Path) -> None:
        distro_data = cls._read_data(path)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])

        ispattern = re.compile(pattern, re.IGNORECASE)
        matched = ispattern.search('')
        for line in lines:
            if line.startswith('Package: '):
                name = line.split('Package: ')[1].rstrip('\n')
                matched = ispattern.search(name)
            elif matched and line.startswith('Filename: '):
                file = line.split('Filename: ')[1].rstrip('\n')
                print(message.format(file))

    @classmethod
    def _grep_full(cls, message: str, pattern: str, path: Path) -> None:
        distro_data = cls._read_data(path)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])

        ispattern = re.compile(pattern, re.IGNORECASE)
        matched = ispattern.search('')
        for line in lines:
            if line.startswith('Package: '):
                name = line.split('Package: ')[1].rstrip('\n')
                matched = ispattern.search(name)
            if matched:
                print(message.format(line))

    @classmethod
    def _search(cls, options: Options) -> None:
        full = options.get_full()
        pattern = options.get_pattern()
        package_files = options.get_packages_file()

        for path in [
            Path(x) for x in package_files if x.endswith('.json.zstd')
        ]:
            message = "{0:s}"
            if len(package_files) > 1:
                message = f"{path}: {message}"
            if full:
                cls._grep_full(message, pattern, path)
            else:
                cls._grep(message, pattern, path)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        cls._search(options)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
