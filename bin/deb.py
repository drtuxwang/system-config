#!/usr/bin/env python3
"""
Make a compressed archive in DEB format or query database/files.
"""

import argparse
import dataclasses
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch, Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_arch(self) -> str:
        """
        Return sub architecture.
        """
        return self._arch

    def get_dpkg(self) -> Command:
        """
        Return dpkg Command class object.
        """
        return self._dpkg

    def get_mode(self) -> str:
        """
        Return operation mode.
        """
        return self._args.mode

    def get_package_names(self) -> List[str]:
        """
        Return list of package names.
        """
        return self._package_names

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make a compressed archive in DEB format or "
            "query database/files.",
        )

        parser.add_argument(
            '-l',
            action='store_const',
            const='list',
            dest='mode',
            default='dpkg',
            help="Show all installed packages (optional arch).",
        )
        parser.add_argument(
            '-d',
            action='store_const',
            const='depends',
            dest='mode',
            default='dpkg',
            help="Show dependency tree for selected installed packages.",
        )
        parser.add_argument(
            '-c',
            action='store_const',
            const='nodepends',
            dest='mode',
            default='dpkg',
            help="Show only installed packages without dependents.",
        )
        parser.add_argument(
            '-s',
            action='store_const',
            const='-s',
            dest='option',
            help="Show status of selected installed packages.",
        )
        parser.add_argument(
            '-L',
            action='store_const',
            const='-L',
            dest='option',
            help="Show files owned by selected installed packages.",
        )
        parser.add_argument(
            '-P',
            action='store_const',
            const='-P',
            dest='option',
            help="Purge selected installed packages.",
        )
        parser.add_argument(
            '-S',
            action='store_const',
            const='-S',
            dest='option',
            help="Locate package which contain file.",
        )
        parser.add_argument(
            '-i',
            action='store_const',
            const='-i',
            dest='option',
            help="Install selected Debian package files.",
        )
        parser.add_argument(
            '-I',
            action='store_const',
            const='-I',
            dest='option',
            help="Show information about selected Debian package files.",
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='package.deb|package|arch',
            help="Debian package file, package name or arch.",
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _file2package(packages: List[str]) -> List[str]:
        """
        Convert deb file names to packages names
        """
        isfile = re.compile('_[^_]*_.*[.]deb')
        return [
            f"{x.split('_')[0]}:{x.split('.deb')[0].split('_')[-1]}"
            if isfile.search(x)
            else x
            for x in packages
        ]

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._dpkg = Command('dpkg', errors='stop')
        self._dpkg.set_args(['--print-architecture'])
        task = Batch(self._dpkg.get_cmdline())
        task.run()
        if len(task.get_output()) != 1:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot detect default "
                "architecture of packages.",
            )
        self._arch = task.get_output()[0]

        if self._args.mode in 'depends':
            self._package_names = self._file2package(self._args.args)
        elif self._args.option:
            self._dpkg.set_args([self._args.option] + (
                self._file2package(self._args.args)
                if self._args.option in ('-s', '-L', '-P')
                else self._args.args
            ))
        elif self._args.args and self._args.args[0].endswith('.deb'):
            self._dpkg = Command('dpkg-deb', errors='stop')
            self._dpkg.set_args(['-b', os.curdir, self._args.args[0]])
        elif self._args.args:
            raise SystemExit(
                f'{sys.argv[0]}: Invalid Debian package name '
                f'"{self._args.args[0]}".',
            )
        elif self._args.mode not in ('list', 'nodepends'):
            self._parse_args(['-h'])
            raise SystemExit(1)


@dataclasses.dataclass
class Package:
    """
    Package class
    """
    version: str = ''
    size: int = -1
    depends: List[str] = dataclasses.field(default_factory=list)
    description: str = ''

    def append_depends(self, name: str) -> None:
        """
        Append to dependency list.

        name = Package name
        """
        self.depends.append(name)

    def get_depends(self) -> List[str]:
        """
        Return depends.
        """
        return self.depends

    def set_depends(self, names: List[str]) -> None:
        """
        Set package dependency list.

        names = List of package names
        """
        self.depends = names

    def get_description(self) -> str:
        """
        Return description.
        """
        return self.description

    def set_description(self, description: str) -> None:
        """
        Set description.

        description = Package description
        """
        self.description = description

    def get_size(self) -> int:
        """
        Return size.
        """
        return self.size

    def set_size(self, size: int) -> None:
        """
        Set size.

        size = Package size
        """
        self.size = size

    def get_version(self) -> str:
        """
        Return version.
        """
        return self.version

    def set_version(self, version: str) -> None:
        """
        Set version.

        version = Package version
        """
        self.version = version


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

    def _read_dpkg_status(self) -> dict:
        packages = {}
        name = ''
        arch = ''
        package = Package()
        try:
            with Path('/var/lib/dpkg/status').open(errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '', 1)
                        arch = ''
                    elif line.startswith('Architecture: '):
                        arch = line.replace('Architecture: ', '', 1)
                    elif line.startswith('Version: '):
                        package.set_version(
                            line.replace('Version: ', '', 1).split(':')[-1]
                        )
                    elif line.startswith('Installed-Size: '):
                        try:
                            package.set_size(
                                int(line.replace('Installed-Size: ', '', 1))
                            )
                        except ValueError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Package "{name}" in '
                                '"/var/lib/dpkg/info" has non integer size.',
                            ) from exception
                    elif line.startswith('Depends: '):
                        for i in line.replace('Depends: ', '', 1).split(', '):
                            package.append_depends(i.split()[0])
                    elif line.startswith('Description: '):
                        package.set_description(
                            line.replace('Description: ', '', 1))
                        packages[f'{name}:{arch}'] = package
                        package = Package()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "/var/lib/dpkg/status" file.',
            ) from exception

        return packages

    def _show_packages_info(self) -> None:
        for key, package in sorted(
            self._packages.items(),
            key=lambda s: s[0].split(':'),
        ):
            name, arch = key.split(':')
            file = f'{name}_{package.get_version()}_{arch}.deb'
            print(
                f"{file:50s}  # "
                f"{package.get_size():5d} KB " f"{package.get_description()}",
            )

    def _show_dependent_packages(
        self,
        package_names: List[str],
        checked: List[str] = None,
        ident: str = '',
    ) -> None:
        if not checked:
            checked = []
        keys = sorted(self._packages)
        for package_name in package_names:
            if ':' in package_name:
                name, arch = package_name.split(':')
            else:
                name = package_name
                arch = (
                    self._arch
                    if f'{name}:{self._arch}' in self._packages
                    else 'all'
                )

            if f'{name}:{arch}' in self._packages:
                print(f"{ident}{name}:{arch}")
                for dep in [
                    x for x in keys if x.endswith((f':{arch}', ':all'))
                ]:
                    if name in self._packages[dep].get_depends():
                        if dep not in checked:
                            checked.append(dep)
                            self._show_dependent_packages(
                                [dep],
                                checked,
                                f'{ident}  '
                            )

    def _show_nodependent_packages(self) -> None:
        all_depends = set()
        for package in self._packages.values():
            all_depends.update(set(package.get_depends()))

        for key, package in sorted(self._packages.items()):
            name, arch = key.split(':')
            if name in all_depends:
                continue
            file = f'{name}_{package.get_version()}_{arch}.deb'
            print(
                f"{file:50s}  # "
                f"{package.get_size():5d} KB {package.get_description()}",
            )

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        self._arch = self._options.get_arch()
        self._packages = self._read_dpkg_status()

        mode = self._options.get_mode()
        if mode == 'list':
            self._show_packages_info()
        elif mode == 'depends':
            for package_name in self._options.get_package_names():
                self._show_dependent_packages([package_name], checked=[])
        elif mode == 'nodepends':
            self._show_nodependent_packages()
        else:
            Exec(self._options.get_dpkg().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
