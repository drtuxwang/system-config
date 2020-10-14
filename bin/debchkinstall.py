#!/usr/bin/env python3
"""
Check installation dependencies of packages against '.debs' list file.
"""

import argparse
import copy
import distutils.version
import glob
import json
import logging
import os
import re
import signal
import sre_constants
import sys

import logging_mod

# pylint: disable = invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable = invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
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
        Return installed packages '.debs' list file.
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
            help='Debian installed packages ".debs" list file.'
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
                '" installed ".debs" list filename.'
            )
        self._distribution = ispattern.sub('', list_file)


class Package:
    """
    Package class
    """

    def __init__(self, depends=(), url=''):
        self._checked_flag = False
        self._installed_flag = False
        self._version = None
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

    def is_newer(self, package):
        """
        Return True if version newer than package.
        """
        try:
            if (
                    distutils.version.LooseVersion(self._version) >
                    distutils.version.LooseVersion(package.get_version())
            ):
                return True
        except TypeError:  # 5.0.0~buster 5.0~rc1~buster
            pass
        return False


class Main:
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
    def _read_data(file):
        try:
            with open(file) as ifile:
                data = json.load(ifile)
        except (OSError, json.decoder.JSONDecodeError) as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            ) from exception

        return data

    @classmethod
    def _read_distribution_packages(cls, packages_file):
        distribution_data = cls._read_data(packages_file)
        lines = []
        for url in distribution_data['urls']:
            lines.extend(distribution_data['data'][url]['text'])

        packages = {}
        name = ''
        package = Package()
        for line in lines:
            line = line.rstrip('\r\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '').split(':')[-1])
            elif line.startswith('Depends: '):
                depends = []
                for i in line.replace('Depends: ', '').split(', '):
                    depends.append(i.split()[0])
                package.set_depends(depends)
            elif line.startswith('Filename: '):
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.set_url(line[10:])
                packages[name] = package
                package = Package()
        return packages

    def _read_distribution_pin_packages(self, pin_file):
        packages_cache = {}
        try:
            with open(pin_file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        pattern = columns[0]
                        if not pattern.startswith('#'):
                            file = os.path.join(os.path.dirname(
                                pin_file), columns[1]) + '.json'
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
                    if not name.startswith('#'):
                        if name in self._packages:
                            self._packages[name].set_installed_flag(True)
        except OSError:
            return

    def _check_package_install(self, distribution, ofile, indent, name):
        if name in self._packages:
            self._packages[name].set_checked_flag(True)
            if self._packages[name].get_installed_flag():
                logger.info(
                    "%s%s [Installed]",
                    indent,
                    self._packages[name].get_url(),
                )
            else:
                file = self._local(
                    distribution,
                    self._packages[name].get_url()
                )
                logger.warning("%s%s", indent, file)
                print(indent + file, file=ofile)
            for i in self._packages[name].get_depends():
                if i in self._packages:
                    if self._packages[i].get_installed_flag():
                        logger.info(
                            "%s  %s [Installed]",
                            indent,
                            self._packages[i].get_url(),
                        )
                    elif (
                            not self._packages[i].get_checked_flag() and
                            not self._packages[name].get_installed_flag()
                    ):
                        self._check_package_install(
                            distribution, ofile, indent + '  ', i)
                    self._packages[i].set_checked_flag(True)

    def _read_distribution_deny_list(self, file):
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if columns:
                        name = columns[0]
                        if not line.strip().startswith('#'):
                            if name in self._packages:
                                if columns[1] == (
                                        '*',
                                        self._packages[name].get_version()
                                ):
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
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + urlfile + '" file.'
            ) from exception
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    @staticmethod
    def _local(distribution, url):
        file = os.path.join(distribution, os.path.basename(url))
        if os.path.isfile(file):
            return 'file://' + os.path.abspath(file)
        return url

    def run(self):
        """
        Start program
        """
        options = Options()

        self._packages = self._read_distribution_packages(
            options.get_distribution() + '.json')
        self._read_distribution_pin_packages(
            options.get_distribution() + '.debs:select')
        self._read_distribution_installed(options.get_list_file())

        ispattern = re.compile('[.]debs-?.*$')
        distribution = ispattern.sub('', options.get_list_file())
        self._read_distribution_deny_list(distribution + '.debs:deny')

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
