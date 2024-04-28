#!/usr/bin/env python3
"""
Check debian directory for old, unused or missing '.deb' packages.
"""

import argparse
import dataclasses
import os
import signal
import sys
from pathlib import Path
from typing import List

from file_mod import FileStat


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_pools(self) -> List[str]:
        """
        Return list of pool directories.
        """
        return self._args.pools

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Check debian directory for old, unused or missing '
            '".deb" packages.',
        )

        parser.add_argument(
            'pools',
            nargs='+',
            metavar='directory',
            help="Pool directory.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


@dataclasses.dataclass
class Package:
    """
    Package class
    """
    file: str
    time: float
    version: str


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
    def _check_files(pool: str) -> dict:
        try:
            paths = sorted(Path(pool).glob('*.deb'))
        except OSError:
            return None
        packages: dict = {}
        for path in paths:
            name = path.name.split('_')[0]
            file_stat = FileStat(path)
            version = path.name.split('_')[1]
            if name in packages:
                if file_stat.get_mtime() > packages[name].time:
                    print(f"rm {packages[name].file}")
                    print(f"#  {path}")
                    packages[name] = Package(
                        str(path),
                        file_stat.get_mtime(),
                        version
                    )
                else:
                    print(f"rm {path}")
                    print(f"#  {packages[name].file}")
            else:
                packages[name] = Package(
                    str(path),
                    file_stat.get_mtime(),
                    version,
                )
        return packages

    @staticmethod
    def _check_used(distribution: str) -> dict:
        packages = {}
        pool = distribution.replace('dist', 'pool')
        try:
            path = Path(f'{distribution}.debs')
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot read corrupt '
                            f'"{path}" package ".debs" list file.',
                        ) from exception
                    packages[name] = Package(
                        f'{pool}/{name}_{version}_*.deb',
                        -1,
                        version,
                    )
        except OSError:
            pass

        try:
            path = Path(f'{distribution}.debs:base')
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot read corrupt '
                            f'"{path}" package ".debs" list file.',
                        ) from exception
                    if name in packages:
                        if packages[name].file == str(
                            Path(pool, f'{name}_{version}_*.deb')
                        ):
                            del packages[name]
        except OSError:
            pass
        return packages

    @staticmethod
    def _read_distribution_allow(file: str) -> dict:
        packages = {}
        try:
            with Path(file).open(errors='replace') as ifile:
                for line in ifile:
                    if not line.strip().startswith('#'):
                        try:
                            name, version = line.split()
                            packages[name] = version
                        except (IndexError, ValueError):
                            pass
        except OSError:
            pass
        return packages

    @staticmethod
    def _compare(
        packages_files: dict,
        packages_allow: dict,
        packages_used: dict,
    ) -> None:
        names_files = sorted(packages_files)
        names_allow_list = sorted(packages_allow)
        names_used = packages_used.keys()

        for name in names_files:
            if name not in names_used:
                if (name in names_allow_list and
                        packages_allow[name] in
                        ('*', packages_files[name])):
                    continue
                print("rm", packages_files[name].file, "# Unused")
            elif packages_files[name].version != packages_used[name].version:
                print("rm", packages_files[name].file, "# Unused")
                print("# ", packages_used[name].file, "Missing")

        for name in names_used:
            if name not in names_files:
                print("# ", packages_used[name].file, "Missing")

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

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        for pool in options.get_pools():
            packages_files = self._check_files(pool)
            distribution = f'{Path(pool).resolve()}'.replace('pool', 'dist')
            if packages_files and Path(f'{distribution}.debs').is_file():
                packages_allow = self._read_distribution_allow(
                    f'{distribution}.debs:allow'
                )
                packages_used = self._check_used(distribution)
                self._compare(
                    packages_files,
                    packages_allow,
                    packages_used
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
