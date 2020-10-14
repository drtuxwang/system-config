#!/usr/bin/env python3
"""
Show information about packages in Debian packages '.debs' list file.
"""

import argparse
import distutils.version
import glob
import json
import os
import signal
import sys


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


class Package:
    """
    Package class
    """

    def __init__(self, version='0', info=()):
        self._version = version
        self._info = info

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

    def get_info(self):
        """
        Return information.
        """
        return self._info

    def set_info(self, info):
        """
        Set package information.
        """
        self._info = info

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
        info = []
        for line in lines:
            line = line.rstrip('\r\n')
            info.append(line)
            if line.startswith('Package: '):
                name = line.replace('Package: ', '')
            elif line.startswith('Version: '):
                package.set_version(
                    line.replace('Version: ', '').split(':')[-1])
            elif not line:
                if name in packages and not package.is_newer(packages[name]):
                    continue
                package.set_info(info)
                packages[name] = package
                info = []
                package = Package()
        return packages

    @staticmethod
    def _show_distribution_packages(packages, package_names):
        for name in package_names:
            if name in packages:
                for line in packages[name].get_info():
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
