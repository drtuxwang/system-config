#!/usr/bin/env python3
"""
Make a compressed archive in DEB format or query database/files.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_arch(self):
        """
        Return sub architecture.
        """
        return self._arch

    def get_arch_sub(self):
        """
        Return sub architecture.
        """
        return self._arch_sub

    def get_dpkg(self):
        """
        Return dpkg Command class object.
        """
        return self._dpkg

    def get_mode(self):
        """
        Return operation mode.
        """
        return self._args.mode

    def get_package_names(self):
        """
        Return list of package names.
        """
        return self._package_names

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make a compressed archive in DEB format or '
            'query database/files.')

        parser.add_argument(
            '-l',
            action='store_const',
            const='list',
            dest='mode',
            default='dpkg',
            help='Show all installed packages (optional arch).'
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
            '-d',
            action='store_const',
            const='depends',
            dest='mode',
            default='dpkg',
            help='Show dependency tree for selected installed packages.'
        )
        parser.add_argument(
            '-P',
            action='store_const',
            const='-P',
            dest='option',
            help='Remove selected installed packages.'
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

    def parse(self, args):
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
        elif self._args.mode == 'depends':
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
            print(
                'usage: deb.py [-h] [-l] [-s] [-L] [-d] [-P] [-S] [-i] [-I]',
                file=sys.stderr
            )
            print(
                '              [package.deb|package|arch '
                '[package.deb|package|arch ...]]',
                file=sys.stderr
            )
            print(
                'deb.py: error: the following arguments are required: '
                'package.deb',
                file=sys.stderr
            )
            raise SystemExit(1)


class Package(object):
    """
    Package class
    """

    def __init__(self, version, size, depends, description):
        self._version = version
        self._size = size
        self._depends = depends
        self._description = description

    def append_depends(self, name):
        """
        Append to dependency list.

        name = Package name
        """
        self._depends.append(name)

    def get_depends(self):
        """
        Return depends.
        """
        return self._depends

    def set_depends(self, names):
        """
        Set package dependency list.

        names = List of package names
        """
        self._depends = names

    def get_description(self):
        """
        Return description.
        """
        return self._description

    def set_description(self, description):
        """
        Set description.

        description = Package description
        """
        self._description = description

    def get_size(self):
        """
        Return size.
        """
        return self._size

    def set_size(self, size):
        """
        Set size.

        size = Package size
        """
        self._size = size

    def get_version(self):
        """
        Return version.
        """
        return self._version

    def set_version(self, version):
        """
        Set version.

        version = Package version
        """
        self._version = version


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def _calc_dependencies(packages, names_all):
        for name, value in packages.items():
            if ':' in name:
                depends = []
                for depend in value.get_depends():
                    if depend.split(':')[0] in names_all:
                        depends.append(depend)
                    else:
                        depends.append(depend + ':' + name.split(':')[-1])
                packages[name].set_depends(depends)

    def _read_dpkg_status(self):
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
                        except ValueError:
                            raise SystemExit(
                                sys.argv[0] + ': Package "' + name +
                                '" in "/var/lib/dpkg/info" has non '
                                'integer size.'
                            )
                    elif line.startswith('Depends: '):
                        for i in line.replace('Depends: ', '', 1).split(', '):
                            package.append_depends(i.split()[0])
                    elif line.startswith('Description: '):
                        package.set_description(
                            line.replace('Description: ', '', 1))
                        packages[name] = package
                        package = Package('', -1, [], '')
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "/var/lib/dpkg/status" file.')

        self._calc_dependencies(packages, names_all)

        return packages

    def _show_packages_info(self):
        for name, package in sorted(self._packages.items()):
            if self._options.get_arch_sub():
                if not name.endswith(self._options.get_arch_sub()):
                    continue
            elif ':' in name:
                continue
            print('{0:35s} {1:15s} {2:5d}KB {3:s}'.format(
                name.split(':')[0], package.get_version(), package.get_size(),
                package.get_description()))

    def _show_dependent_packages(self, names, checked=None, ident=''):
        if not checked:
            checked = []
        keys = sorted(self._packages.keys())
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

    def run(self):
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
        else:
            subtask_mod.Exec(self._options.get_dpkg().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
