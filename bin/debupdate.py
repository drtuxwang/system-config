#!/usr/bin/env python3
"""
Check whether installed debian packages in '.debs' list have updated versions.
"""

import argparse
import copy
import dataclasses
import json
import logging
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

import pyzstd  # type: ignore

from command_mod import LooseVersion
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
    version: str = '0'
    depends: List[str] = dataclasses.field(default_factory=list)
    url: str = ''

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

        packages: dict = {}
        disable_deps = re.fullmatch(r'.*_\w+-\w+.json', str(path))
        name = ''
        arch = ''
        package = Package()
        for line in lines:
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
                            path = Path(
                                pin_path.parent,
                                f'{columns[1]}.json.zst',
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

    def _read_distro_deny_list(self, path: Path) -> None:
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        name = columns[0]
                        if not line.strip().startswith('#'):
                            if name in self._packages:
                                if (
                                    columns[1] == '*' or
                                    columns[1] == self._packages[name].version
                                ):
                                    del self._packages[name]
        except OSError:
            pass

    def _read_distro_installed(self, path: Path) -> dict:
        versions = {}
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    file = line.split('#')[0].strip().split()[0]
                    try:
                        name, version, arch = file[:-4].split('_')
                    except IndexError:
                        continue
                    versions[f'{name}:{arch}'] = version
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.',
            ) from exception
        return versions

    def _check_distro_updates(self, distro: str, path: Path,) -> None:
        versions = self._read_distro_installed(path)

        url_path = Path(
            f"{Path(distro).name}{str(path).rsplit('.debs', 1)[-1]}.url"
        )
        pool = distro.replace('dist', 'pool')
        try:
            with url_path.open('w') as ofile:
                for name, version in sorted(versions.items()):
                    if name in self._packages:
                        new_version = self._packages[name].version
                        if new_version != version:
                            file = self._local(pool, self._packages[name].url)
                            logger.info(
                                "Update: %s (%s => %s)",
                                name,
                                version,
                                new_version,
                            )
                            logger.info("  %s", file)
                            print(f"{file}  # {version}", file=ofile)
                            for dependency in sorted(self._depends(
                                versions,
                                self._packages[name].depends,
                                name.split(':')[-1],
                            )):
                                if dependency in self._packages:
                                    file = self._local(
                                        pool,
                                        self._packages[dependency].url,
                                    )
                                    logger.warning("    %s", file)
                                    print(f"  {file}", file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{url_path}" file.',
            ) from exception
        if url_path.stat().st_size == 0:
            url_path.unlink()

    def _depends(
        self,
        versions: dict,
        depends: List[str],
        arch: str,
    ) -> List[str]:
        names = []
        if depends:
            for name in depends:
                for depend in set([f'{name}:{arch}', f'{name}:all']):
                    if depend not in versions:
                        versions[depend] = ''
                        names.append(depend)
                        if depend in self._packages:
                            names.extend(self._depends(
                                versions,
                                self._packages[depend].depends,
                                arch,
                            ))
        return names

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

        ispattern = re.compile('[.]debs-?.*')
        for path in [Path(x) for x in options.get_list_files()]:
            if not path.is_file():
                logger.error('Cannot find "%s" list file.', path)
                continue
            if path.stat().st_size > 0:
                if ispattern.search(str(path)):
                    distro = ispattern.sub('', str(path))
                    logger.info('Checking "%s" list file.', path)
                    self._packages = self._read_distro_packages(
                        Path(f'{distro}.json.zst')
                    )
                    self._read_distro_pin_packages(
                        Path(f'{distro}.debs:select')
                    )
                    self._read_distro_deny_list(Path(f'{distro}.debs:deny'))
                    self._check_distro_updates(distro, path)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
