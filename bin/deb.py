#!/usr/bin/env python3
"""
Make a compressed archive in DEB format or query database/files.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


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

    def get_arch_sub(self) -> str:
        """
        Return sub architecture.
        """
        return self._arch_sub

    def get_dpkg(self) -> command_mod.Command:
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
            description='Make a compressed archive in DEB format or '
            'query database/files.',
        )

        parser.add_argument(
            '-l',
            action='store_const',
            const='list',
            dest='mode',
            default='dpkg',
            help='Show all installed packages (optional arch).'
        )
        parser.add_argument(
            '-d',
            action='store_const',
            const='depends',
            dest='mode',
            default='dpkg',
            help='Show dependency tree for selected installed packages.'
        )
        parser.add_argument(
            '-c',
            action='store_const',
            const='nodepends',
            dest='mode',
            default='dpkg',
            help='Show only installed packages without dependents.'
        )
        parser.add_argument(
            '-s',
            action='store_const',
            const='-s',
            dest='option',
            help='Show status of selected installed packages.'
        )
        parser.add_argument(
            '-L',
            action='store_const',
            const='-L',
            dest='option',
            help='Show files owned by selected installed packages.'
        )
        parser.add_argument(
            '-P',
            action='store_const',
            const='-P',
            dest='option',
            help='Purge selected installed packages.'
        )
        parser.add_argument(
            '-S',
            action='store_const',
            const='-S',
            dest='option',
            help='Locate package which contain file.'
        )
        parser.add_argument(
            '-i',
            action='store_const',
            const='-i',
            dest='option',
            help='Install selected Debian package files.'
        )
        parser.add_argument(
            '-I',
            action='store_const',
            const='-I',
            dest='option',
            help='Show information about selected Debian package files.'
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='package.deb|package|arch',
            help='Debian package file, package name or arch.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._dpkg = command_mod.Command('dpkg', errors='stop')
        self._dpkg.set_args(['--print-architecture'])
        task = subtask_mod.Batch(self._dpkg.get_cmdline())
        task.run()
        if len(task.get_output()) != 1:
            raise SystemExit(
                sys.argv[0] + ": Cannot detect default architecture of "
                "packages."
            )
        self._arch = task.get_output()[0]

        if self._args.mode == 'list':
            if self._args.args:
                self._arch_sub = self._args.args[0]
            else:
                self._arch_sub = ''
        elif self._args.mode in ('depends', 'nodepends'):
            self._package_names = self._args.args
        elif self._args.option:
            self._dpkg.set_args([self._args.option] + self._args.args)
        elif self._args.args and self._args.args[0].endswith('.deb'):
            self._dpkg = command_mod.Command('dpkg-deb', errors='stop')
            self._dpkg.set_args(['-b', os.curdir, self._args.args[0]])
        elif self._args.args:
            raise SystemExit(
                sys.argv[0] + ': Invalid Debian package name "' +
                self._args.args[0] + '".'
            )
        else:
            self._parse_args(['-h'])
            raise SystemExit(1)


class Package:
    """
    Package class
    """

    def __init__(
        self,
        version: str,
        size: int,
        depends: List[str],
        description: str,
    ) -> None:
        self._version = version
        self._size = size
        self._depends = depends
        self._description = description

    def append_depends(self, name: str) -> None:
        """
        Append to dependency list.

        name = Package name
        """
        self._depends.append(name)

    def get_depends(self) -> List[str]:
        """
        Return depends.
        """
        return self._depends

    def set_depends(self, names: List[str]) -> None:
        """
        Set package dependency list.

        names = List of package names
        """
        self._depends = names

    def get_description(self) -> str:
        """
        Return description.
        """
        return self._description

    def set_description(self, description: str) -> None:
        """
        Set description.

        description = Package description
        """
        self._description = description

    def get_size(self) -> int:
        """
        Return size.
        """
        return self._size

    def set_size(self, size: int) -> None:
        """
        Set size.

        size = Package size
        """
        self._size = size

    def get_version(self) -> str:
        """
        Return version.
        """
        return self._version

    def set_version(self, version: str) -> None:
        """
        Set version.

        version = Package version
        """
        self._version = version


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
    def _calc_dependencies(packages: dict, names_all: List[str]) -> None:
        for name, value in packages.items():
            if ':' in name:
                depends = []
                for depend in value.get_depends():
                    if depend.split(':')[0] in names_all:
                        depends.append(depend)
                    else:
                        depends.append(depend + ':' + name.split(':')[-1])
                packages[name].set_depends(depends)

    def _read_dpkg_status(self) -> dict:
        names_all = []

        packages = {}
        name = ''
        package = Package('', -1, [], '')
        try:
            with open('/var/lib/dpkg/status', errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\r\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '', 1)
                    elif line.startswith('Architecture: '):
                        arch = line.replace('Architecture: ', '', 1)
                        if arch == 'all':
                            names_all.append(name)
                        elif arch != self._options.get_arch():
                            name += ':' + arch
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
                                '" in "/var/lib/dpkg/info" has non '
                                'integer size.'
                            ) from exception
                    elif line.startswith('Depends: '):
                        for i in line.replace('Depends: ', '', 1).split(', '):
                            package.append_depends(i.split()[0])
                    elif line.startswith('Description: '):
                        package.set_description(
                            line.replace('Description: ', '', 1))
                        packages[name] = package
                        package = Package('', -1, [], '')
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "/var/lib/dpkg/status" file.'
            ) from exception

        self._calc_dependencies(packages, names_all)

        return packages

    def _show_packages_info(self) -> None:
        for name, package in sorted(self._packages.items()):
            if self._options.get_arch_sub():
                if not name.endswith(self._options.get_arch_sub()):
                    continue
            elif ':' in name:
                continue
            print("{0:35s} {1:15s} {2:5d}KB {3:s}".format(
                name.split(':')[0],
                package.get_version(),
                package.get_size(),
                package.get_description()
            ))

    def _show_dependent_packages(
        self,
        names: List[str],
        checked: List[str] = None,
        ident: str = '',
    ) -> None:
        if not checked:
            checked = []
        keys = sorted(self._packages)
        for name in names:
            if name in self._packages:
                print(ident + name)
                for key in keys:
                    if name in self._packages[key].get_depends():
                        if key not in checked:
                            checked.append(key)
                            self._show_dependent_packages(
                                [key],
                                checked,
                                ident + '  '
                            )

    def _show_nodependent_packages(self) -> None:
        keys = sorted(self._packages)

        for name in keys:
            package = self._packages.get(name)
            if package:
                for key in keys:
                    if name in self._packages[key].get_depends():
                        break
                else:
                    print("{0:35s} {1:15s} {2:5d}KB {3:s}".format(
                        name.split(':')[0],
                        package.get_version(),
                        package.get_size(),
                        package.get_description()
                    ))

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        self._packages = self._read_dpkg_status()

        mode = self._options.get_mode()
        if mode == 'list':
            self._show_packages_info()
        elif mode == 'depends':
            for packagename in self._options.get_package_names():
                self._show_dependent_packages([packagename], checked=[])
        elif mode == 'nodepends':
            self._show_nodependent_packages()
        else:
            subtask_mod.Exec(self._options.get_dpkg().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
