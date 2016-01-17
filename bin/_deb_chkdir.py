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

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

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
            packagesFiles = self._check_files(distribution)
            if packagesFiles and os.path.isfile(distribution + '.debs'):
                packagesWhiteList = self._read_distribution_whitelist(distribution + '.whitelist')
                packagesUsed = self._check_used(distribution)
                self._compare(packagesFiles, packagesWhiteList, packagesUsed)

    def _check_files(self, distribution):
        try:
            files = sorted(glob.glob(os.path.join(distribution, '*.deb')))
        except OSError:
            return
        packages = {}
        for file in files:
            name = os.path.basename(file).split('_')[0]
            fileStat = syslib.FileStat(file)
            version = os.path.basename(file).split('_')[1]
            if name in packages:
                if fileStat.get_time() > packages[name].get_time():
                    print('rm', packages[name].get_file())
                    print('# ', file)
                    packages[name] = Package(file, fileStat.get_time(), version)
                else:
                    print('rm', file)
                    print('# ', packages[name].get_file())
            else:
                packages[name] = Package(file, fileStat.get_time(), version)
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
        except IOError:
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
        except IOError:
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
        except IOError:
            pass
        return packages

    def _compare(self, packagesFiles, packagesWhiteList, packagesUsed):
        namesFiles = sorted(packagesFiles.keys())
        namesWhiteList = sorted(packagesWhiteList.keys())
        namesUsed = packagesUsed.keys()

        for name in namesFiles:
            if name not in namesUsed:
                if (name in namesWhiteList and packagesWhiteList[name] in (
                        '*', packagesFiles[name])):
                    continue
                print('rm', packagesFiles[name].get_file(), '# Unused')
            elif packagesFiles[name].get_version() != packagesUsed[name].get_version():
                print('rm', packagesFiles[name].get_file(), '# Unused')
                print('# ', packagesUsed[name].get_file(), 'Missing')

        for name in namesUsed:
            if name not in namesFiles:
                print('# ', packagesUsed[name].get_file(), 'Missing')


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
