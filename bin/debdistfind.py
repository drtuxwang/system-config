#!/usr/bin/env python3
"""
Search for packages that match regular expression in Debian package file.
"""

import argparse
import glob
import json
import os
import re
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_packages_file(self):
        """
        Return packages file location.
        """
        return self._args.packages_file[0]

    def get_patterns(self):
        """
        Return list of regular expression search patterns.
        """
        return self._args.patterns

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Search for packages that match regular '
            'expression in Debian package file.'
        )

        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.json',
            help='Debian package file.'
        )
        parser.add_argument(
            'patterns',
            nargs='+',
            metavar='pattern',
            help='Regular expression.'
        )

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

    def __init__(self, version, size, description):
        self._version = version
        self._size = size
        self._description = description

    def get_description(self):
        """
        Return description.
        """
        return self._description

    def set_description(self, description):
        """
        Set package description.
        """
        self._description = description

    def get_size(self):
        """
        Return size.
        """
        return self._size

    def set_size(self, size):
        """
        Set package size.
        """
        self._size = size

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
            self._packages = {}
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

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

    def _read_distribution_packages(self, packages_file):
        distribution_data = self._read_data(packages_file)
        lines = []
        for url in distribution_data['urls']:
            lines.extend(distribution_data['data'][url]['text'])

        self._packages = {}
        name = ''
        package = Package('', -1, '')
        for line in lines:
            line = line.rstrip('\r\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
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
                        '" in "/var/lib/dpkg/info" has non integer size.'
                    )
            elif line.startswith('Description: '):
                package.set_description(
                    line.replace('Description: ', '', 1))
                self._packages[name] = package
                package = Package('', 0, '')

    def _search_distribution_packages(self, patterns):
        for pattern in patterns:
            ispattern = re.compile(pattern, re.IGNORECASE)
            for name, package in sorted(self._packages.items()):
                if ispattern.search(name) or ispattern.search(
                        self._packages[name].get_description()
                ):
                    print("{0:25s} {1:15s} {2:5d}KB {3:s}".format(
                        name.split(':')[0],
                        package.get_version(),
                        package.get_size(),
                        package.get_description()
                    ))

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

        self._read_distribution_packages(options.get_packages_file())
        self._search_distribution_packages(options.get_patterns())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
