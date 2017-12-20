#!/usr/bin/env python3
"""
Check debian directory for old, unused or missing '.deb' packages.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_distributions(self):
        """
        Return list of distributions directories.
        """
        return self._args.distributions

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check debian directory for old, unused or missing '
            '".deb" packages.'
        )

        parser.add_argument(
            'distributions',
            nargs='+',
            metavar='directory',
            help='Distribution directory.'
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

    def __init__(self, file, time, version):
        self._file = file
        self._time = time
        self._version = version

    def get_file(self):
        """
        Return package file location.
        """
        return self._file

    def get_time(self):
        """
        Return package time stamp.
        """
        return self._time

    def get_version(self):
        """
        Return version.
        """
        return self._version


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
    def _check_files(distribution):
        try:
            files = sorted(glob.glob(os.path.join(distribution, '*.deb')))
        except OSError:
            return
        packages = {}
        for file in files:
            name = os.path.basename(file).split('_')[0]
            file_stat = file_mod.FileStat(file)
            version = os.path.basename(file).split('_')[1]
            if name in packages:
                if file_stat.get_time() > packages[name].get_time():
                    print("rm", packages[name].get_file())
                    print("# ", file)
                    packages[name] = Package(
                        file,
                        file_stat.get_time(),
                        version
                    )
                else:
                    print("rm", file)
                    print("# ", packages[name].get_file())
            else:
                packages[name] = Package(file, file_stat.get_time(), version)
        return packages

    @staticmethod
    def _check_used(distribution):
        packages = {}
        try:
            file = distribution + '.debs'
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot read corrupt "' + file +
                            '" package ".debs" list file.'
                        )
                    packages[name] = Package(os.path.join(
                        distribution,
                        name + '_' + version + '_*.deb'
                    ), -1, version)
        except OSError:
            pass

        try:
            file = distribution + '.baselist'
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot read corrupt "' + file +
                            '" package ".debs" list file.'
                        )
                    if name in packages:
                        if packages[name].get_file() == os.path.join(
                                distribution,
                                name + '_' + version + '_*.deb'
                        ):
                            del packages[name]
        except OSError:
            pass
        return packages

    @staticmethod
    def _read_distribution_whitelist(file):
        packages = {}
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    if line[:1] != '#':
                        try:
                            name, version = line.split()
                            packages[name] = version
                        except (IndexError, ValueError):
                            pass
        except OSError:
            pass
        return packages

    @staticmethod
    def _compare(packages_files, packages_white_list, packages_used):
        names_files = sorted(packages_files.keys())
        names_white_list = sorted(packages_white_list.keys())
        names_used = packages_used.keys()

        for name in names_files:
            if name not in names_used:
                if (name in names_white_list and
                        packages_white_list[name] in
                        ('*', packages_files[name])):
                    continue
                print("rm", packages_files[name].get_file(), "# Unused")
            elif (
                    packages_files[name].get_version() !=
                    packages_used[name].get_version()
            ):
                print("rm", packages_files[name].get_file(), "# Unused")
                print("# ", packages_used[name].get_file(), "Missing")

        for name in names_used:
            if name not in names_files:
                print("# ", packages_used[name].get_file(), "Missing")

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

        for distribution in options.get_distributions():
            packages_files = self._check_files(distribution)
            if packages_files and os.path.isfile(distribution + '.debs'):
                packages_white_list = self._read_distribution_whitelist(
                    distribution + '.whitelist')
                packages_used = self._check_used(distribution)
                self._compare(
                    packages_files,
                    packages_white_list,
                    packages_used
                )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
