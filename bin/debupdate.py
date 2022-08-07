#!/usr/bin/env python3
"""
Check whether installed debian packages in '.debs' list have updated versions.
"""

import argparse
import copy
import glob
import json
import logging
import os
import re
import signal
import sre_constants
import sys
from typing import List

import packaging.version

import logging_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Package:
    """
    Package class
    """

    def __init__(
        self,
        version: str = '0',
        depends: List[str] = None,
        url: str = '',
    ) -> None:
        self._version = version
        self._depends = depends if depends else []
        self._url = url

    def get_depends(self) -> List[str]:
        """
        Return list of required dependent packages.
        """
        return self._depends

    def set_depends(self, depends: List[str]) -> None:
        """
        Set list of required dependent packages.

        depends = List of required dependent packages
        """
        self._depends = depends

    def get_url(self) -> str:
        """
        Return package url.
        """
        return self._url

    def set_url(self, url: str) -> None:
        """
        Set package url.

        url = Package url
        """
        self._url = url

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

    @staticmethod
    def _get_loose_version(version: str) -> packaging.version.LegacyVersion:
        """
        Return LegacyVersion object
        """
        return packaging.version.LegacyVersion(version.replace('+', '.x'))

    def is_newer(self, package: 'Package') -> bool:
        """
        Return True if version newer than package.
        """
        if (
            self._get_loose_version(self._version) >
            self._get_loose_version(package.get_version())
        ):
            return True
        return False


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_list_files(self) -> List[str]:
        """
        Return list of installed packages files.
        """
        return self._args.list_files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Check whether installed debian packages in '
            '".debs" list have updated versions.',
        )

        parser.add_argument(
            'list_files',
            nargs='+',
            metavar='distro.debs',
            help='Debian installed packages ".debs" list file.',
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
    def _read_distro_packages(cls, packages_file: str) -> dict:
        distro_data = cls._read_data(packages_file)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])

        packages: dict = {}
        name = ''
        package = Package()
        for line in lines:
            line = line.rstrip('\r\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '').split(':')[-1])
            elif line.startswith('Depends: '):
                depends = []
                for i in line.replace('Depends: ', '').split(', '):
                    depends.append(i.split()[0])
                package.set_depends(depends)
            elif line.startswith('Filename: '):
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.set_url(line[10:])
                packages[name] = package
                package = Package()
        return packages

    def _read_distro_pin_packages(self, pin_file: str) -> None:
        packages_cache = {}
        try:
            with open(pin_file, encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        pattern = columns[0]
                        if not pattern.startswith('#'):
                            file = os.path.join(
                                os.path.dirname(pin_file),
                                columns[1]
                            ) + '.json'
                            if file not in packages_cache:
                                packages_cache[file] = (
                                    self._read_distro_packages(file))
                            try:
                                ispattern = re.compile(pattern.replace(
                                    '?', '.').replace('*', '.*'))
                            except sre_constants.error:
                                continue
                            for key, value in packages_cache[file].items():
                                if ispattern.fullmatch(key):
                                    self._packages[key] = copy.copy(value)
        except OSError:
            pass

    def _read_distro_deny_list(self, file: str) -> None:
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        name = columns[0]
                        if not line.strip().startswith('#'):
                            if name in self._packages:
                                if (columns[1] == '*' or
                                        columns[1] ==
                                        self._packages[name].get_version()):
                                    del self._packages[name]
        except OSError:
            return

    def _check_distro_updates(
        self,
        distro: str,
        list_file: str,
    ) -> None:
        try:
            with open(list_file, encoding='utf-8', errors='replace') as ifile:
                versions = {}
                for line in ifile:
                    if not line.startswith('#'):
                        try:
                            name, version = line.split()[:2]
                        except ValueError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Format error in '
                                f'"{os.path.join(distro, list_file)}".',
                            ) from exception
                        versions[name] = version
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{list_file}" file.',
            ) from exception

        urlfile = (
            os.path.basename(distro) + list_file.split('.debs')[-1]+'.url'
        )
        try:
            with open(urlfile, 'w', encoding='utf-8', newline='\n') as ofile:
                for name, version in sorted(versions.items()):
                    if name in self._packages:
                        new_version = self._packages[name].get_version()
                        if new_version != version:
                            file = self._local(
                                distro,
                                self._packages[name].get_url()
                            )
                            logger.info(
                                "Update: %s (%s => %s)",
                                name,
                                version,
                                new_version,
                            )
                            logger.info("  %s", file)
                            print(
                                f"# Update: {name} "
                                f"({version} => "
                                f"{new_version})",
                                file=ofile,
                            )
                            print(file, file=ofile)
                            for dependency in sorted(self._depends(
                                    versions,
                                    self._packages[name].get_depends()
                            )):
                                if dependency in self._packages:
                                    file = self._local(
                                        distro,
                                        self._packages[dependency].get_url()
                                    )
                                    logger.warning("    %s", file)
                                    print(f"  {file}", file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{urlfile}" file.',
            ) from exception
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _depends(self, versions: dict, depends: List[str]) -> List[str]:
        names = []
        if depends:
            for name in depends:
                if name not in versions:
                    versions[name] = ''
                    names.append(name)
                    if name in self._packages:
                        names.extend(self._depends(
                            versions,
                            self._packages[name].get_depends()
                        ))
        return names

    @staticmethod
    def _local(distro: str, url: str) -> str:
        file = os.path.join(distro, os.path.basename(url))
        if os.path.isfile(file):
            return f'file://{os.path.abspath(file)}'
        return url

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        ispattern = re.compile('[.]debs-?.*')
        for list_file in options.get_list_files():
            if not os.path.isfile(list_file):
                logger.error('Cannot find "%s" list file.', list_file)
                continue
            if os.path.getsize(list_file) > 0:
                if os.path.isfile(list_file):
                    if ispattern.search(list_file):
                        distro = ispattern.sub('', list_file)
                        logger.info('Checking "%s" list file.', list_file)
                        self._packages = self._read_distro_packages(
                            distro + '.json')
                        self._read_distro_pin_packages(
                            distro + '.debs:select')
                        self._read_distro_deny_list(
                            distro + '.debs:deny')
                        self._check_distro_updates(
                            distro, list_file)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
