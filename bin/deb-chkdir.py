#!/usr/bin/env python3
"""
Check debian directory for old, unused or missing '.deb' packages.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDistributions(self):
        """
        Return list of distributions directories.
        """
        return self._args.distributions

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Check debian directory for old, unused or missing ".deb" packages.')

        parser.add_argument('distributions', nargs='+', metavar='directory',
                            help='Distribution directory.')

        self._args = parser.parse_args(args)


class Package(syslib.Dump):

    def __init__(self, file, time, version):
        self._file = file
        self._time = time
        self._version = version

    def getFile(self):
        """
        Return package file location.
        """
        return self._file

    def getTime(self):
        """
        Return package time stamp.
        """
        return self._time

    def getVersion(self):
        """
        Return version.
        """
        return self._version


class CheckDistributions(syslib.Dump):

    def __init__(self, options):
        for distribution in options.getDistributions():
            packagesFiles = self._checkFiles(distribution)
            if packagesFiles and os.path.isfile(distribution + '.debs'):
                packagesWhiteList = self._readDistributionWhitelist(distribution + '.whitelist')
                packagesUsed = self._checkUsed(distribution)
                self._compare(packagesFiles, packagesWhiteList, packagesUsed)

    def _checkFiles(self, distribution):
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
                if fileStat.getTime() > packages[name].getTime():
                    print('rm', packages[name].getFile())
                    print('# ', file)
                    packages[name] = Package(file, fileStat.getTime(), version)
                else:
                    print('rm', file)
                    print('# ', packages[name].getFile())
            else:
                packages[name] = Package(file, fileStat.getTime(), version)
        return packages

    def _checkUsed(self, distribution):
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
                        if (packages[name].getFile() ==
                                os.path.join(distribution, name + '_' + version + '_*.deb')):
                            del packages[name]
        except IOError:
            pass
        return packages

    def _readDistributionWhitelist(self, file):
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
                print('rm', packagesFiles[name].getFile(), '# Unused')
            elif packagesFiles[name].getVersion() != packagesUsed[name].getVersion():
                print('rm', packagesFiles[name].getFile(), '# Unused')
                print('# ', packagesUsed[name].getFile(), 'Missing')

        for name in namesUsed:
            if name not in namesFiles:
                print('# ', packagesUsed[name].getFile(), 'Missing')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
