#!/usr/bin/env python3
"""
Search for packages that match regular expression in Debian package file.
"""

# Annotation: Fix Class reference run time NameError
from __future__ import annotations
import argparse
import distutils.version
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

    def get_check_all(self) -> bool:
        """
        Return check all (including description).
        """
        return self._args.check_all

    def get_packages_file(self) -> str:
        """
        Return packages file location.
        """
        return self._args.packages_file[0]

    def get_patterns(self) -> List[str]:
        """
        Return list of regular expression search patterns.
        """
        return self._args.patterns

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Search for packages that match regular '
            'expression in Debian package file.',
        )

        parser.add_argument(
            '-a',
            dest='check_all',
            action='store_true',
            help='Check description as well.'
        )
        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.json',
            help='Debian package file.'
        )
        parser.add_argument(
            'patterns',
            nargs='+',
            metavar='pattern',
            help='Regular expression.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Package:
    """
    Package class
    """

    def __init__(self, version: str, size: int, description: str) -> None:
        self._version = version
        self._size = size
        self._description = description

    def get_description(self) -> str:
        """
        Return description.
        """
        return self._description

    def set_description(self, description: str) -> None:
        """
        Set package description.
        """
        self._description = description

    def get_size(self) -> int:
        """
        Return size.
        """
        return self._size

    def set_size(self, size: int) -> None:
        """
        Set package size.
        """
        self._size = size

    def get_version(self) -> str:
        """
        Return version.
        """
        return self._version

    def set_version(self, version: str) -> None:
        """
        Set package version.

        version = package version.
        """
        self._version = version

    def is_newer(self, package: Package) -> bool:
        """
        Return True if version newer than package.
        """
        try:
            if (
                    distutils.version.LooseVersion(self._version) >
                    distutils.version.LooseVersion(package.get_version())
            ):
                return True
        except TypeError:  # 5.0.0~buster 5.0~rc1~buster
            pass
        return False


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
    def _read_data(file: str) -> dict:
        try:
            with open(file) as ifile:
                data = json.load(ifile)
        except (OSError, json.decoder.JSONDecodeError) as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            ) from exception

        return data

    @classmethod
    def _read_distribution_packages(cls, packages_file: str) -> dict:
        distribution_data = cls._read_data(packages_file)
        lines = []
        for url in distribution_data['urls']:
            lines.extend(distribution_data['data'][url]['text'])

        packages: dict = {}
        name = ''
        package = Package('', -1, '')
        for line in lines:
            line = line.rstrip('\r\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '', 1).split(':')[-1])
            elif line.startswith('Installed-Size: '):
                try:
                    package.set_size(
                        int(line.replace('Installed-Size: ', '', 1)))
                except ValueError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Package "' + name +
                        '" in "/var/lib/dpkg/info" has non integer size.'
                    ) from exception
            elif line.startswith('Description: '):
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.set_description(
                    line.replace('Description: ', '', 1))
                packages[name] = package
                package = Package('', 0, '')
        return packages

    @staticmethod
    def _search_distribution_packages(
        packages: dict,
        patterns: List[str],
        check_all: bool = False,
    ) -> None:
        for pattern in patterns:
            ispattern = re.compile(pattern, re.IGNORECASE)
            for name, package in sorted(packages.items()):
                if (
                        ispattern.search(name) or
                        check_all and ispattern.search(
                            packages[name].get_description()
                        )
                ):
                    print("{0:25s} {1:15s} {2:5d}KB {3:s}".format(
                        name.split(':')[0],
                        package.get_version(),
                        package.get_size(),
                        package.get_description()
                    ))

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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        packages = self._read_distribution_packages(
            options.get_packages_file()
        )
        self._search_distribution_packages(
            packages,
            options.get_patterns(),
            options.get_check_all()
        )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
