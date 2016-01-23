#!/usr/bin/env python3
"""
Check debian directory for old, unused or missing '.deb' packages.
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

    def get_distributions(self):
        """
        Return list of distributions directories.
        """
        return self._args.distributions

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check debian directory for old, unused or missing ".deb" packages.')

        parser.add_argument('distributions', nargs='+', metavar='directory',
                            help='Distribution directory.')

        self._args = parser.parse_args(args)


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


class CheckDistributions(object):
    """
    Check distribution class
    """

    def __init__(self, options):
        for distribution in options.get_distributions():
            packages_files = self._check_files(distribution)
            if packages_files and os.path.isfile(distribution + '.debs'):
                packages_white_list = self._read_distribution_whitelist(distribution + '.whitelist')
                packages_used = self._check_used(distribution)
                self._compare(packages_files, packages_white_list, packages_used)

    def _check_files(self, distribution):
        try:
            files = sorted(glob.glob(os.path.join(distribution, '*.deb')))
        except OSError:
            return
        packages = {}
        for file in files:
            name = os.path.basename(file).split('_')[0]
            file_stat = syslib.FileStat(file)
            version = os.path.basename(file).split('_')[1]
            if name in packages:
                if file_stat.get_time() > packages[name].get_time():
                    print('rm', packages[name].get_file())
                    print('# ', file)
                    packages[name] = Package(file, file_stat.get_time(), version)
                else:
                    print('rm', file)
                    print('# ', packages[name].get_file())
            else:
                packages[name] = Package(file, file_stat.get_time(), version)
        return packages

    def _check_used(self, distribution):
        packages = {}
        try:
            file = distribution + '.debs'
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError:
                        raise SystemExit(sys.argv[0] + ': Cannot read corrupt "' + file +
                                         '" package list file.')
                    packages[name] = Package(os.path.join(
                        distribution, name + '_' + version + '_*.deb'), -1, version)
        except OSError:
            pass

        try:
            file = distribution + '.baselist'
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        name, version = line.split()[:2]
                    except ValueError:
                        raise SystemExit(sys.argv[0] + ': Cannot read corrupt "' + file +
                                         '" package list file.')
                    if name in packages:
                        if (packages[name].get_file() ==
                                os.path.join(distribution, name + '_' + version + '_*.deb')):
                            del packages[name]
        except OSError:
            pass
        return packages

    def _read_distribution_whitelist(self, file):
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

    def _compare(self, packages_files, packages_white_list, packages_used):
        names_files = sorted(packages_files.keys())
        names_white_list = sorted(packages_white_list.keys())
        names_used = packages_used.keys()

        for name in names_files:
            if name not in names_used:
                if (name in names_white_list and packages_white_list[name] in (
                        '*', packages_files[name])):
                    continue
                print('rm', packages_files[name].get_file(), '# Unused')
            elif packages_files[name].get_version() != packages_used[name].get_version():
                print('rm', packages_files[name].get_file(), '# Unused')
                print('# ', packages_used[name].get_file(), 'Missing')

        for name in names_used:
            if name not in names_files:
                print('# ', packages_used[name].get_file(), 'Missing')


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
            CheckDistributions(options)
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
