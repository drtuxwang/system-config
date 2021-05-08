#!/usr/bin/env python3
"""
Show information about packages in Debian packages '.debs' list file.
"""

# Annotation: Fix Class reference run time NameError
from __future__ import annotations
import argparse
import distutils.version
import glob
import json
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

    def get_packages_file(self) -> str:
        """
        Return packages file location.
        """
        return self._args.packages_file[0]

    def get_package_names(self) -> List[str]:
        """
        Return list of package names.
        """
        return self._args.package_names

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Show information about packages in Debian '
            'packages ".debs" list file.',
        )

        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.json',
            help='Debian package ".debs" list file.'
        )
        parser.add_argument(
            'package_names',
            nargs='+',
            metavar='package',
            help='Package name.'
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

    def __init__(self, version: str = '0', info: List[str] = None) -> None:
        self._version = version
        self._info = info

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

    def get_info(self) -> List[str]:
        """
        Return information.
        """
        return self._info

    def set_info(self, info: List[str]) -> None:
        """
        Set package information.
        """
        self._info = info

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
        package = Package()
        info = []
        for line in lines:
            line = line.rstrip('\r\n')
            info.append(line)
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '').split(':')[-1])
            elif not line:
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.set_info(info)
                packages[name] = package
                info = []
                package = Package()
        return packages

    @staticmethod
    def _show_distribution_packages(
        packages: dict,
        package_names: List[str],
    ) -> None:
        for name in package_names:
            if name in packages:
                for line in packages[name].get_info():
                    print(line)
                print()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        packages = cls._read_distribution_packages(options.get_packages_file())
        cls._show_distribution_packages(packages, options.get_package_names())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
