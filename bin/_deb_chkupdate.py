#!/usr/bin/env python3
"""
Check whether installed debian packages in '.debs' list have updated versions.
"""

import argparse
import copy
import glob
import os
import re
import signal
import sre_constants
import sys

import file_utility

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_list_files(self):
        """
        Return list of installed packages files.
        """
        return self._args.list_files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Check whether installed debian packages in '
                                                     '".debs" list have updated versions.')

        parser.add_argument('list_files', nargs='+', metavar='distribution.debs',
                            help='Debian installed packages list file.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Package(object):
    """
    Package class
    """

    def __init__(self, version='0', depends=(), url=''):
        self._version = version
        self._depends = depends
        self._url = url

    def get_depends(self):
        """
        Return list of required dependent packages.
        """
        return self._depends

    def set_depends(self, depends):
        """
        Set list of required dependent packages.

        depends = List of required dependent packages
        """
        self._depends = depends

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

    def get_version(self):
        """
        Return version.
        """
        return self._version

    def set_version(self, version):
        """
        Set package version.

        version = package version.
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
                    elif line.startswith('Version: '):
                        package.set_version(line.replace('Version: ', '').split(':')[-1])
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
            raise SystemExit(sys.argv[0] + ': Cannot open "' + packages_file + '" packages file.')
        return packages

    def _read_distribution_pin_packages(self, pin_file):
        packages_cache = {}
        try:
            with open(pin_file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        pattern = columns[0]
                        if pattern[:1] != '#':
                            file = os.path.join(os.path.dirname(pin_file), columns[1]) + '.packages'
                            if file not in packages_cache:
                                packages_cache[file] = self._read_distribution_packages(file)
                            try:
                                ispattern = re.compile(
                                    pattern.replace('?', '.').replace('*', '.*')+'$')
                            except sre_constants.error:
                                continue
                            for key, value in packages_cache[file].items():
                                if ispattern.match(key):
                                    self._packages[key] = copy.copy(value)
        except OSError:
            pass

    def _read_distribution_blacklist(self, file):
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        name = columns[0]
                        if name[:1] != '#':
                            if name in self._packages:
                                if (columns[1] == '*' or
                                        columns[1] == self._packages[name].get_version()):
                                    del self._packages[name]
        except OSError:
            return

    def _check_distribution_updates(self, distribution, list_file):
        try:
            with open(list_file, errors='replace') as ifile:
                versions = {}
                for line in ifile:
                    if line[:1] != '#':
                        try:
                            name, version = line.split()[:2]
                        except ValueError:
                            raise SystemExit(sys.argv[0] + ': Format error in "' +
                                             os.path.join(distribution, 'packages.ilist') + '".')
                        versions[name] = version
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + list_file + '" file.')

        urlfile = os.path.basename(distribution) + list_file.split('.debs')[-1]+'.url'
        try:
            with open(urlfile, 'w', newline='\n') as ofile:
                for name, version in sorted(versions.items()):
                    if name in self._packages:
                        if self._packages[name].get_version() != version:
                            file = self._local(distribution, self._packages[name].get_url())
                            print(file, '(Replaces', version + ')')
                            print(file, file=ofile)
                            for name in sorted(
                                    self._depends(versions, self._packages[name].get_depends())):
                                if name in self._packages:
                                    file = self._local(distribution, self._packages[name].get_url())
                                    print('  ' + file, '(New dependency)')
                                    print('  ' + file, file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _depends(self, versions, depends):
        names = []
        for name in depends:
            if name not in versions:
                versions[name] = ''
                names.append(name)
                if name in self._packages:
                    names.extend(self._depends(versions, self._packages[name].get_depends()))
        return names

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

        ispattern = re.compile('[.]debs-?.*$')
        for list_file in options.get_list_files():
            if file_utility.FileStat(list_file).get_size() > 0:
                if os.path.isfile(list_file):
                    if ispattern.search(list_file):
                        distribution = ispattern.sub('', list_file)
                        print('\nChecking "' + list_file + '" list file...')
                        self._packages = self._read_distribution_packages(
                            distribution + '.packages')
                        self._read_distribution_pin_packages(distribution + '.pinlist')
                        self._read_distribution_blacklist(distribution + '.blacklist')
                        self._check_distribution_updates(distribution, list_file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
