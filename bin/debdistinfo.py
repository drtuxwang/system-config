#!/usr/bin/env python3
"""
Show information about packages in Debian packages '.debs' list file.
"""

import argparse
import glob
import json
import os
import signal
import sys


if sys.version_info < (3, 5) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.5, < 4.0).")


class Options:
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
            'packages ".debs" list file.'
        )

        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.json',
            help='Debian package ".debs" list file.'
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
        for line in lines:
            line = line.rstrip('\r\n')
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
                lines = [line]
            elif line:
                lines.append(line)
            else:
                packages[name] = lines
        return packages

    @staticmethod
    def _show_distribution_packages(packages, package_names):
        for name in package_names:
            if name in packages:
                for line in packages[name]:
                    print(line)
                print()

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        packages = cls._read_distribution_packages(options.get_packages_file())
        cls._show_distribution_packages(packages, options.get_package_names())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
