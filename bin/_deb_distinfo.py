#!/usr/bin/env python3
"""
Show information about packages in Debian packages list file.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

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
        return self._args.packages_file[0]

    def get_package_names(self):
        """
        Return list of package names.
        """
        return self._args.package_names

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show information about packages in Debian packages list file.')

        parser.add_argument('packages_file', nargs=1, metavar='distribution.package',
                            help='Debian package list file.')
        parser.add_argument('package_names', nargs='+', metavar='package', help='Package name.')

        self._args = parser.parse_args(args)


class Info(object):
    """
    Information class
    """

    def __init__(self, options):
        self._read_distribution_packages(options.get_packages_file())
        self._show_distribution_packages(options.get_package_names())

    def _read_distribution_packages(self, packages_file):
        self._packages = {}
        name = ''
        lines = []
        try:
            with open(packages_file, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\r\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '')
                        lines = [line]
                    elif line:
                        lines.append(line)
                    else:
                        self._packages[name] = lines
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + packages_file + '" packages file.')

    def _show_distribution_packages(self, package_names):
        for name in package_names:
            if name in self._packages:
                for line in self._packages[name]:
                    print(line)
                print()


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
            Info(options)
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
