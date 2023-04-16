#!/usr/bin/env python3
"""
Check installation dependencies of packages against '.debs' list file.
"""

import argparse
import dataclasses
import copy
import json
import logging
import os
import re
import signal
import sys
from pathlib import Path
from typing import List, TextIO

import pyzstd

import command_mod
import logging_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


@dataclasses.dataclass
class Package:
    """
    Package class
    """
    depends: List[str] = dataclasses.field(default_factory=list)
    url: str = ''
    version: str = None
    installed: bool = False
    checked: bool = False

    def is_newer(self, package: 'Package') -> bool:
        """
        Return True if version newer than package.
        """
        if (
            command_mod.LooseVersion(self.version) >
            command_mod.LooseVersion(package.version)
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

    def get_distro(self) -> str:
        """
        Return distro name.
        """
        return self._distro

    def get_list_file(self) -> str:
        """
        Return installed packages '.debs' list file.
        """
        return self._args.list_file[0]

    def get_package_names(self) -> List[str]:
        """
        Return list of package names.
        """
        return self._args.packageNames

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Check installation dependencies of packages '
            'against ".debs" list file.',
        )

        parser.add_argument(
            'list_file',
            nargs=1,
            metavar='distro.debs',
            help='Debian installed packages ".debs" list file.',
        )
        parser.add_argument(
            'packageNames',
            nargs='+',
            metavar='package',
            help="Debian package name.",
        )

        self._args = parser.parse_args(args[1:])

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args)

        list_file = self._args.list_file[0]
        ispattern = re.compile('[.]debs-?.*$')
        if not ispattern.search(list_file):
            raise SystemExit(
                f'{sys.argv[0]}: Invalid "{list_file}" '
                'installed ".debs" list filename.',
            )
        self._distro = ispattern.sub('', list_file)


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
    def _read_distro_packages(cls, path: Path) -> dict:
        distro_data = cls._read_data(path)
        lines = []
        for url in distro_data['urls']:
            lines.extend(distro_data['data'][url]['text'])
        disable_deps = re.fullmatch(r'.*_\w+-\w+.json', str(path))

        packages: dict = {}
        name = ''
        package = Package()
        for line in lines:
            line = line.rstrip('\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.version = line.replace('Version: ', '').split(':')[-1]
            elif line.startswith('Depends: '):
                if not disable_deps:
                    depends = []
                    for i in line.replace('Depends: ', '').split(', '):
                        depends.append(i.split()[0])
                    package.depends = depends
            elif line.startswith('Filename: '):
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.url = line[10:]
                packages[name] = package
                package = Package()
        return packages

    def _read_distro_pin_packages(self, pin_path: Path) -> None:
        packages_cache = {}
        try:
            with pin_path.open(errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        pattern = columns[0]
                        if not pattern.startswith('#'):
                            path = Path(
                                pin_path.parent,
                                f'{columns[1]}.json.zstd',
                            )
                            if path not in packages_cache:
                                packages_cache[path] = (
                                    self._read_distro_packages(path)
                                )
                            ispattern = re.compile(
                                pattern.replace('?', '.').replace('*', '.*')
                            )
                            for key, value in packages_cache[path].items():
                                if ispattern.fullmatch(key):
                                    self._packages[key] = copy.copy(value)
        except OSError:
            pass

    def _read_distro_installed(self, installed_file: str) -> None:
        try:
            with Path(installed_file).open(errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    name = columns[0]
                    if not name.startswith('#'):
                        if name in self._packages:
                            self._packages[name].installed = True
        except OSError:
            return

    def _check_package_install(
        self,
        distro: str,
        ofile: TextIO,
        indent: str,
        name: str,
    ) -> None:
        if name in self._packages:
            self._packages[name].checked = True
            if self._packages[name].installed:
                logger.info(
                    "%s%s [Installed]",
                    indent,
                    self._packages[name].url,
                )
            else:
                pool = distro.replace('dist', 'pool')
                file = self._local(pool, self._packages[name].url)
                logger.warning("%s%s", indent, file)
                print(f"{indent}{file}", file=ofile)
            for i in self._packages[name].depends:
                if i in self._packages:
                    if self._packages[i].installed:
                        logger.info(
                            "%s  %s [Installed]",
                            indent,
                            self._packages[i].url,
                        )
                    elif (
                        not self._packages[i].checked and
                        not self._packages[name].installed
                    ):
                        self._check_package_install(
                            distro,
                            ofile,
                            f"{indent}  ",
                            i,
                        )
                    self._packages[i].checked = True

    def _read_distro_deny_list(self, file: str) -> None:
        try:
            with Path(file).open(errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        name = columns[0]
                        if not line.strip().startswith('#'):
                            if name in self._packages:
                                if columns[1] == (
                                    '*',
                                    self._packages[name].version
                                ):
                                    del self._packages[name]
        except OSError:
            return

    def _check_distro_install(
        self,
        distro: str,
        list_file: str,
        names: List[str],
    ) -> None:
        path = Path(f"{Path(distro).name}{list_file.split('.debs')[-1]}.url")
        try:
            with path.open('w') as ofile:
                indent = ''
                for i in names:
                    self._check_package_install(distro, ofile, indent, i)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{path}" file.',
            ) from exception
        if path.stat().st_size == 0:
            os.remove(path)

    @staticmethod
    def _local(pool: str, url: str) -> str:
        path = Path(pool, Path(url).name)
        if path.is_file():
            return f'file://{path.resolve()}'
        return url

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._packages = self._read_distro_packages(
            Path(f'{options.get_distro()}.json.zstd')
        )
        self._read_distro_pin_packages(
            Path(f'{options.get_distro()}.debs:select')
        )
        self._read_distro_installed(options.get_list_file())

        ispattern = re.compile('[.]debs-?.*$')
        distro = ispattern.sub('', options.get_list_file())
        self._read_distro_deny_list(distro + '.debs:deny')

        self._check_distro_install(
            options.get_distro(),
            options.get_list_file(),
            options.get_package_names()
        )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
