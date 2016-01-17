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

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        listFile = self._args.listFile[0]
        ispattern = re.compile('[.]debs-?.*$')
        if not ispattern.search(listFile):
            raise SystemExit(sys.argv[0] + ': Invalid "' + listFile + '" installed list filename.')
        self._distribution = ispattern.sub('', listFile)

    def get_distribution(self):
        """
        Return distribution name.
        """
        return self._distribution

    def get_list_file(self):
        """
        Return installed packages list file.
        """
        return self._args.listFile[0]

    def get_package_names(self):
        """
        Return list of package names.
        """
        return self._args.packageNames

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check installation dependencies of packages against ".debs" list file.')

        parser.add_argument('listFile', nargs=1, metavar='distribution.debs',
                            help='Debian installed packages list file.')
        parser.add_argument('packageNames', nargs='+', metavar='package',
                            help='Debian package name.')

        self._args = parser.parse_args(args)


class Package(object):
    """
    Package class
    """

    def __init__(self, depends=[], url=''):
        self._checked_flag = False
        self._installed_flag = False
        self._depends = depends
        self._url = url

    def get_checked_flag(self):
        """
        Return packaged checked flag.
        """
        return self._checked_flag

    def set_checked_flag(self, checkedFlag):
        """
        Set package checked flag.

        checkedFlag = Package checked flag
        """
        self._checked_flag = checkedFlag

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

    def set_installed_flag(self, installedFlag):
        """
        Set package installed flag.

        installedFlag = Package installed flag
        """
        self._installed_flag = installedFlag

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


class CheckInstall(object):
    """
    Check install class
    """

    def __init__(self, options):
        self._packages = self._read_distribution_packages(options.get_distribution() + '.packages')
        self._read_distribution_pin_packages(options.get_distribution() + '.pinlist')
        self._read_distribution_installed(options.get_list_file())
        self._check_distribution_install(
            options.get_distribution(), options.get_list_file(), options.get_package_names())

    def _read_distribution_packages(self, packagesFile):
        packages = {}
        name = ''
        package = Package()
        try:
            with open(packagesFile, errors='replace') as ifile:
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
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + packagesFile + '" packages file.')
        return packages

    def _read_distribution_pin_packages(self, pinFile):
        packagesCache = {}
        try:
            with open(pinFile, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        pattern = columns[0]
                        if pattern[:1] != '#':
                            file = os.path.join(os.path.dirname(pinFile), columns[1]) + '.packages'
                            if file not in packagesCache:
                                packagesCache[file] = self._read_distribution_packages(file)
                            try:
                                ispattern = re.compile(
                                    pattern.replace('?', '.').replace('*', '.*')+'$')
                            except sre_constants.error:
                                continue
                            for key, value in packagesCache[file].items():
                                if ispattern.match(key):
                                    self._packages[key] = copy.copy(packagesCache[file][key])
        except IOError:
            pass

    def _read_distribution_installed(self, installedFile):
        try:
            with open(installedFile, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    name = columns[0]
                    if name[:1] != '#':
                        if name in self._packages:
                            self._packages[name].set_installed_flag(True)
        except IOError:
            return

    def _check_package_install(self, distribution, ofile, indent, name):
        if name in self._packages:
            self._packages[name].set_checked_flag(True)
            if self._packages[name].get_installed_flag():
                print(indent + self._packages[name].get_url(), '[Installed]')
            else:
                file = self._local(distribution, self._packages[name].get_url())
                print(indent + file)
                print(indent + file, file=ofile)
            for i in self._packages[name].get_depends():
                if i in self._packages:
                    if self._packages[i].get_installed_flag():
                        print(indent + '  ' + self._packages[i].get_url(), '[Installed]')
                    elif self._packages[i].get_checked_flag():
                        print(indent + '  ' + self._packages[i].get_url())
                    elif not self._packages[name].get_installed_flag():
                        self._check_package_install(distribution, ofile, indent + '  ', i)

    def _check_distribution_install(self, distribution, listFile, names):
        urlfile = os.path.basename(distribution) + listFile.split('.debs')[-1] + '.url'
        try:
            with open(urlfile, 'w', newline='\n') as ofile:
                indent = ''
                for i in names:
                    self._check_package_install(distribution, ofile, indent, i)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _local(self, distribution, url):
        file = os.path.join(distribution, os.path.basename(url))
        if os.path.isfile(file):
            return 'file://' + os.path.abspath(file)
        return url


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            CheckInstall(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
