#!/usr/bin/env python3
"""
Check installation dependencies of packages.
"""

import argparse
import dataclasses
import copy
import logging
import os
import re
import signal
import sys
from pathlib import Path
from typing import List, TextIO

from command_mod import LooseVersion
from debian_mod import DebianDist
from logging_mod import ColoredFormatter

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
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
        if LooseVersion(self.version) > LooseVersion(package.version):
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
        return self._packages

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
        ispattern = re.compile('[.]debs(-.*)?$')
        if not ispattern.search(list_file):
            raise SystemExit(
                f'{sys.argv[0]}: Invalid "{list_file}" '
                'installed ".debs" list filename.',
            )
        self._distro = ispattern.sub('', list_file)

        isfile = re.compile('_[^_]*_.*[.]deb')
        self._packages = [
            f"{x.split('_')[0]}:{x.split('.deb')[0].split('_')[-1]}"
            if isfile.search(x)
            else x
            for x in self._args.packageNames
        ]


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

    @classmethod
    def _read_distro_packages(cls, path: Path) -> dict:
        disable_deps = re.fullmatch(r'.*_\w+-\w+.dist', str(path))
        packages: dict = {}
        name = ''
        arch = ''
        package = Package()
        for line in DebianDist(path).get():
            line = line.rstrip('\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
            elif line.startswith('Architecture: '):
                arch = line.replace('Architecture: ', '', 1)
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
                existing_package = packages.get(f'{name}:{arch}')
                if (
                    not existing_package or
                    LooseVersion(existing_package.version) <
                    LooseVersion(package.version)
                ):
                    packages[f'{name}:{arch}'] = package
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
                            path = Path(pin_path.parent, f'{columns[1]}.dist')
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
                    try:
                        name, _, arch = line.split('.deb')[0].split('_')
                    except IndexError:
                        continue
                    if f'{name}:{arch}' in self._packages:
                        self._packages[f'{name}:{arch}'].installed = True
        except OSError:
            pass

    def _check_package_install(
        self,
        distro: str,
        ofile: TextIO,
        indent: str,
        package_name: str,
    ) -> None:
        if ':' not in package_name:
            package_name = (
                f'{package_name}:{self._arch}'
                if f'{package_name}:{self._arch}' in self._packages
                else f'{package_name}:all'
            )

        if package_name in self._packages:
            _, arch = package_name.split(':')
            self._packages[package_name].checked = True
            pool = distro.replace('dist', 'pool')
            file = self._local(pool, self._packages[package_name].url)
            if self._packages[package_name].installed:
                logger.warning("%s%s [Installed]", indent, file)
                if not indent:
                    print(f"{indent}{file}  # Reinstall", file=ofile)
            else:
                logger.warning("%s%s", indent, file)
                print(f"{indent}{file}", file=ofile)

            for dep in [
                f'{x}:{arch}'
                if f'{x}:{arch}' in self._packages else f'{x}:all'
                for x in self._packages[package_name].depends
            ]:
                if dep in self._packages:
                    if self._packages[dep].installed:
                        logger.info(
                            "%s  %s [Installed]",
                            indent,
                            self._packages[dep].url,
                        )
                    elif (
                        not self._packages[dep].checked and
                        not self._packages[package_name].installed
                    ):
                        self._check_package_install(
                            distro,
                            ofile,
                            f"{indent}  ",
                            dep,
                        )
                    self._packages[dep].checked = True

    def _read_distro_deny_list(self, path: Path) -> None:
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version, arch = (
                            line.rsplit('.deb', 1)[0].split('_')
                        )
                    except (IndexError, ValueError):
                        continue
                    package = f'{name}:{arch}'
                    if (
                        package in self._packages and
                        version in ('*', self._packages[package].version)
                    ):
                        del self._packages[package]
        except OSError:
            pass

    def _check_distro_install(
        self,
        distro: str,
        list_file: str,
        packages_names: List[str],
    ) -> None:
        path = Path(f"{Path(distro).name}{list_file.split('.debs')[-1]}.url")
        try:
            with path.open('w') as ofile:
                indent = ''
                for packages_name in packages_names:
                    self._check_package_install(
                        distro,
                        ofile,
                        indent,
                        packages_name,
                    )
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

        distro = options.get_distro()
        self._packages = self._read_distro_packages(Path(f'{distro}.dist'))
        self._read_distro_pin_packages(Path(f'{distro}.debs:select'))
        self._read_distro_installed(options.get_list_file())
        self._arch = distro.split('_')[-1]

        ispattern = re.compile('[.]debs(-.*)?$')
        distro = ispattern.sub('', options.get_list_file())
        self._read_distro_deny_list(Path(f'{distro}.debs:deny'))

        self._check_distro_install(
            distro,
            options.get_list_file(),
            options.get_package_names()
        )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
