#!/usr/bin/env python3
"""
Search for packages that match regular expression in Debian package file.
"""

import argparse
import glob
import os
import re
import signal
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

    def get_packages_file(self):
        """
        Return packages file location.
        """
        return self._args.packagesFile[0]

    def get_patterns(self):
        """
        Return list of regular expression search patterns.
        """
        return self._args.patterns

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Search for packages that match regular '
                                                     'expression in Debian package file.')

        parser.add_argument('packagesFile', nargs=1, metavar='distribution.package',
                            help='Debian package file.')
        parser.add_argument('patterns', nargs='+', metavar='pattern',
                            help='Regular expression.')

        self._args = parser.parse_args(args)


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

    def getSize(self):
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


class Search(object):
    """
    Search class
    """

    def __init__(self, options):
        self._read_distribution_packages(options.get_packages_file())
        self._search_distribution_packages(options.get_patterns())

    def _read_distribution_packages(self, packagesFile):
        self._packages = {}
        name = ''
        package = Package('', -1, '')
        try:
            with open(packagesFile, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\r\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '')
                    elif line.startswith('Version: '):
                        package.set_version(line.replace('Version: ', '', 1).split(':')[-1])
                    elif line.startswith('Installed-Size: '):
                        try:
                            package.set_size(int(line.replace('Installed-Size: ', '', 1)))
                        except ValueError:
                            raise SystemExit(sys.argv[0] + ': Package "' + name +
                                             '" in "/var/lib/dpkg/info" has non integer size.')
                    elif line.startswith('Description: '):
                        package.set_description(line.replace('Description: ', '', 1))
                        self._packages[name] = package
                        package = Package('', '0', '')
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + packagesFile + '" packages file.')

    def _search_distribution_packages(self, patterns):
        for pattern in patterns:
            ispattern = re.compile(pattern, re.IGNORECASE)
            for name, package in sorted(self._packages.items()):
                if (ispattern.search(name) or
                        ispattern.search(self._packages[name].get_description())):
                    print('{0:25s} {1:15s} {2:5d}KB {3:s}'.format(name.split(':')[0],
                          package.get_version(), package.getSize(), package.get_description()))


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
            Search(options)
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
