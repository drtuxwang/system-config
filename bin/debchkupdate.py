#!/usr/bin/env python3
"""
Check whether installed debian packages in '.debs' list have updated versions.
"""

import argparse
import copy
import glob
import json
import logging
import os
import re
import signal
import sre_constants
import sys

import logging_mod

if sys.version_info < (3, 5) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.5, < 4.0).")

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

    def get_list_files(self):
        """
        Return list of installed packages files.
        """
        return self._args.list_files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check whether installed debian packages in '
            '".debs" list have updated versions.'
        )

        parser.add_argument(
            'list_files',
            nargs='+',
            metavar='distribution.debs',
            help='Debian installed packages ".debs" list file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Package:
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
        except (OSError, json.decoder.JSONDecodeError):
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            )

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
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '').split(':')[-1])
            elif line.startswith('Depends: '):
                depends = []
                for i in line.replace('Depends: ', '').split(', '):
                    depends.append(i.split()[0])
                package.set_depends(depends)
            elif line.startswith('Filename: '):
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
                        if pattern[:1] != '#':
                            file = os.path.join(
                                os.path.dirname(pin_file),
                                columns[1]
                            ) + '.json'
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

    def _check_distribution_updates(self, distribution, list_file):
        try:
            with open(list_file, errors='replace') as ifile:
                versions = {}
                for line in ifile:
                    if line[:1] != '#':
                        try:
                            name, version = line.split()[:2]
                        except ValueError:
                            raise SystemExit(
                                sys.argv[0] + ': Format error in "' +
                                os.path.join(distribution, list_file) + '".')
                        versions[name] = version
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + list_file + '" file.')

        urlfile = os.path.basename(
            distribution) + list_file.split('.debs')[-1]+'.url'
        try:
            with open(urlfile, 'w', newline='\n') as ofile:
                for name, version in sorted(versions.items()):
                    if name in self._packages:
                        if self._packages[name].get_version() != version:
                            file = self._local(
                                distribution,
                                self._packages[name].get_url()
                            )
                            logger.info("%s (Replaces %s)", file, version)
                            print(file, file=ofile)
                            for dependency in sorted(self._depends(
                                    versions,
                                    self._packages[name].get_depends()
                            )):
                                if dependency in self._packages:
                                    file = self._local(
                                        distribution,
                                        self._packages[dependency].get_url()
                                    )
                                    logger.warning(
                                        "  %s (New dependency)",
                                        file,
                                    )
                                    print("  " + file, file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _depends(self, versions, depends):
        names = []
        for name in depends:
            if name not in versions:
                versions[name] = ''
                names.append(name)
                if name in self._packages:
                    names.extend(self._depends(
                        versions,
                        self._packages[name].get_depends()
                    ))
        return names

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

        ispattern = re.compile('[.]debs-?.*$')
        for list_file in options.get_list_files():
            if not os.path.isfile(list_file):
                logger.error('Cannot find "%s" list file.', list_file)
                continue
            if os.path.getsize(list_file) > 0:
                if os.path.isfile(list_file):
                    if ispattern.search(list_file):
                        distribution = ispattern.sub('', list_file)
                        logger.info('Checking "%s" list file.', list_file)
                        self._packages = self._read_distribution_packages(
                            distribution + '.json')
                        self._read_distribution_pin_packages(
                            distribution + '.debs-pinlist')
                        self._read_distribution_blacklist(
                            distribution + '.debs-blacklist')
                        self._check_distribution_updates(
                            distribution, list_file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
