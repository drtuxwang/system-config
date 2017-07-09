#!/usr/bin/env python3
"""
Check installation dependencies of packages against '.debs' list file.
"""

import argparse
import copy
import glob
import os
import re
import signal
import sre_constants
import sys


if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_distribution(self):
        """
        Return distribution name.
        """
        return self._distribution

    def get_list_file(self):
        """
        Return installed packages list file.
        """
        return self._args.list_file[0]

    def get_package_names(self):
        """
        Return list of package names.
        """
        return self._args.packageNames

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check installation dependencies of packages '
            'against ".debs" list file.'
        )

        parser.add_argument(
            'list_file',
            nargs=1,
            metavar='distribution.debs',
            help='Debian installed packages list file.'
        )
        parser.add_argument(
            'packageNames',
            nargs='+',
            metavar='package',
            help='Debian package name.'
        )

        self._args = parser.parse_args(args[1:])

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args)

        list_file = self._args.list_file[0]
        ispattern = re.compile('[.]debs-?.*$')
        if not ispattern.search(list_file):
            raise SystemExit(
                sys.argv[0] + ': Invalid "' + list_file +
                '" installed list filename.'
            )
        self._distribution = ispattern.sub('', list_file)


class Package(object):
    """
    Package class
    """

    def __init__(self, depends=(), url=''):
        self._checked_flag = False
        self._installed_flag = False
        self._depends = depends
        self._url = url

    def get_checked_flag(self):
        """
        Return packaged checked flag.
        """
        return self._checked_flag

    def set_checked_flag(self, checked_flag):
        """
        Set package checked flag.

        checked_flag = Package checked flag
        """
        self._checked_flag = checked_flag

    def get_depends(self):
        """
        Return list of required dependent packages.
        """
        return self._depends

    def set_depends(self, names):
        """
        Set package dependency list.

        names = List of package names
        """
        self._depends = names

    def get_installed_flag(self):
        """
        Return package installed flag.
        """
        return self._installed_flag

    def set_installed_flag(self, installed_flag):
        """
        Set package installed flag.

        installed_flag = Package installed flag
        """
        self._installed_flag = installed_flag

    def get_url(self):
        """
        Return package url.
        """
        return self._url

    def set_url(self, url):
        """
        Set package url.

        url = Package url
        """
        self._url = url


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
    def _read_distribution_packages(packages_file):
        packages = {}
        name = ''
        package = Package()
        try:
            with open(packages_file, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\r\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '')
                    elif line.startswith('Depends: '):
                        depends = []
                        for i in line.replace('Depends: ', '').split(', '):
                            depends.append(i.split()[0])
                        package.set_depends(depends)
                    elif line.startswith('Filename: '):
                        package.set_url(line[10:])
                        packages[name] = package
                        package = Package()
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + packages_file +
                '" packages file.'
            )
        return packages

    def _read_distribution_pin_packages(self, pin_file):
        packages_cache = {}
        try:
            with open(pin_file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        pattern = columns[0]
                        if pattern[:1] != '#':
                            file = os.path.join(os.path.dirname(
                                pin_file), columns[1]) + '.packages'
                            if file not in packages_cache:
                                packages_cache[file] = (
                                    self._read_distribution_packages(file))
                            try:
                                ispattern = re.compile(pattern.replace(
                                    '?', '.').replace('*', '.*')+'$')
                            except sre_constants.error:
                                continue
                            for key, value in packages_cache[file].items():
                                if ispattern.match(key):
                                    self._packages[key] = copy.copy(value)
        except OSError:
            pass

    def _read_distribution_installed(self, installed_file):
        try:
            with open(installed_file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    name = columns[0]
                    if name[:1] != '#':
                        if name in self._packages:
                            self._packages[name].set_installed_flag(True)
        except OSError:
            return

    def _check_package_install(self, distribution, ofile, indent, name):
        if name in self._packages:
            self._packages[name].set_checked_flag(True)
            if self._packages[name].get_installed_flag():
                print(indent + self._packages[name].get_url(), '[Installed]')
            else:
                file = self._local(
                    distribution,
                    self._packages[name].get_url()
                )
                print(indent + file)
                print(indent + file, file=ofile)
            for i in self._packages[name].get_depends():
                if i in self._packages:
                    if self._packages[i].get_installed_flag():
                        print(
                            indent + '  ' + self._packages[i].get_url(),
                            '[Installed]'
                        )
                    elif (
                            not self._packages[i].get_checked_flag() and
                            not self._packages[name].get_installed_flag()
                    ):
                        self._check_package_install(
                            distribution, ofile, indent + '  ', i)
                    self._packages[i].set_checked_flag(True)

    def _read_distribution_blacklist(self, file):
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        name = columns[0]
                        if name[:1] != '#':
                            if name in self._packages:
                                if (columns[1] == '*' or
                                        columns[1] ==
                                        self._packages[name].get_version()):
                                    del self._packages[name]
        except OSError:
            return

    def _check_distribution_install(self, distribution, list_file, names):
        urlfile = os.path.basename(
            distribution) + list_file.split('.debs')[-1] + '.url'
        try:
            with open(urlfile, 'w', newline='\n') as ofile:
                indent = ''
                for i in names:
                    self._check_package_install(distribution, ofile, indent, i)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    @staticmethod
    def _local(distribution, url):
        file = os.path.join(distribution, os.path.basename(url))
        if os.path.isfile(file):
            return 'file://' + os.path.abspath(file)
        return url

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

    def run(self):
        """
        Start program
        """
        options = Options()

        self._packages = self._read_distribution_packages(
            options.get_distribution() + '.packages')
        self._read_distribution_pin_packages(
            options.get_distribution() + '.pinlist')
        self._read_distribution_installed(options.get_list_file())

        ispattern = re.compile('[.]debs-?.*$')
        distribution = ispattern.sub('', options.get_list_file())
        self._read_distribution_blacklist(
             distribution + '.blacklist')

        self._check_distribution_install(
            options.get_distribution(),
            options.get_list_file(),
            options.get_package_names()
        )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
