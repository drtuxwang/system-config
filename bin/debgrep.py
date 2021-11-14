#!/usr/bin/env python3
"""
Search Debian package json file.
"""

# Annotation: Fix Class reference run time NameError
import argparse
import glob
import json
import os
import re
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
            metavar='distro.json',
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
    def _read_data(file: str) -> dict:
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                data = json.load(ifile)
        except (OSError, json.decoder.JSONDecodeError) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{file}" json file.',
            ) from exception

        return data

    @classmethod
    def _grep(cls, message: str, pattern: str, file: str) -> None:
        distro_data = cls._read_data(file)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])

        ispattern = re.compile(pattern, re.IGNORECASE)
        matched = ispattern.search('')
        for line in lines:
            if line.startswith('Package: '):
                name = line.split('Package: ')[1].rstrip('\r\n')
                matched = ispattern.search(name)
            elif matched and line.startswith('Filename: '):
                file = line.split('Filename: ')[1].rstrip('\r\n')
                print(message.format(file))

    @classmethod
    def _grep_full(cls, message: str, pattern: str, file: str) -> None:
        distro_data = cls._read_data(file)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])

        ispattern = re.compile(pattern, re.IGNORECASE)
        matched = ispattern.search('')
        for line in lines:
            if line.startswith('Package: '):
                name = line.split('Package: ')[1].rstrip('\r\n')
                matched = ispattern.search(name)
            if matched:
                print(message.format(line))

    @classmethod
    def _search(cls, options: Options) -> None:
        full = options.get_full()
        pattern = options.get_pattern()
        package_files = options.get_packages_file()

        for file in package_files:
            message = "{0:s}"
            if len(package_files) > 1:
                message = f"{file}: {message}"
            if full:
                cls._grep_full(message, pattern, file)
            else:
                cls._grep(message, pattern, file)

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
