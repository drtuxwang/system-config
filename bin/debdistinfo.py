#!/usr/bin/env python3
"""
Show information about packages in Debian packages list file.
"""

import argparse
import glob
import os
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

    def get_package_names(self):
        """
        Return list of package names.
        """
        return self._args.package_names

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show information about packages in Debian '
            'packages list file.'
        )

        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.package',
            help='Debian package list file.'
        )
        parser.add_argument(
            'package_names',
            nargs='+',
            metavar='package',
            help='Package name.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + packages_file +
                '" packages file.'
            )

    def _show_distribution_packages(self, package_names):
        for name in package_names:
            if name in self._packages:
                for line in self._packages[name]:
                    print(line)
                print()

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
        self._show_distribution_packages(options.get_package_names())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
