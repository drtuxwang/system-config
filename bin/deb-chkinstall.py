#!/usr/bin/env python3
"""
Check installation dependencies of packages against '.debs' list file.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import copy
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        listFile = self._args.listFile[0]
        ispattern = re.compile('[.]debs-?.*$')
        if not ispattern.search(listFile):
            raise SystemExit(sys.argv[0] + ': Invalid "' + listFile + '" installed list filename.')
        self._distribution = ispattern.sub('', listFile)

    def getDistribution(self):
        """
        Return distribution name.
        """
        return self._distribution

    def getListFile(self):
        """
        Return installed packages list file.
        """
        return self._args.listFile[0]

    def getPackageNames(self):
        """
        Return list of package names.
        """
        return self._args.packageNames

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Check installation dependencies of packages against ".debs" list file.')

        parser.add_argument('listFile', nargs=1, metavar='distribution.debs',
                            help='Debian installed packages list file.')
        parser.add_argument('packageNames', nargs='+', metavar='package',
                            help='Debian package name.')

        self._args = parser.parse_args(args)


class Package(syslib.Dump):

    def __init__(self, depends=[], url=''):
        self._checkedFlag = False
        self._installedFlag = False
        self._depends = depends
        self._url = url

    def getCheckedFlag(self):
        """
        Return packaged checked flag.
        """
        return self._checkedFlag

    def setCheckedFlag(self, checkedFlag):
        """
        Set package checked flag.

        checkedFlag = Package checked flag
        """
        self._checkedFlag = checkedFlag

    def getDepends(self):
        """
        Return list of required dependent packages.
        """
        return self._depends

    def setDepends(self, names):
        """
        Set package dependency list.

        names = List of package names
        """
        self._depends = names

    def getInstalledFlag(self):
        """
        Return package installed flag.
        """
        return self._installedFlag

    def setInstalledFlag(self, installedFlag):
        """
        Set package installed flag.

        installedFlag = Package installed flag
        """
        self._installedFlag = installedFlag

    def getUrl(self):
        """
        Return package url.
        """
        return self._url

    def setUrl(self, url):
        """
        Set package url.

        url = Package url
        """
        self._url = url


class CheckInstall(syslib.Dump):

    def __init__(self, options):
        self._packages = self._readDistributionPackages(options.getDistribution() + '.packages')
        self._readDistributionPinPackages(options.getDistribution() + '.pinlist')
        self._readDistributionInstalled(options.getListFile())
        self._checkDistributionInstall(options.getDistribution(), options.getListFile(),
                                       options.getPackageNames())

    def _readDistributionPackages(self, packagesFile):
        packages = {}
        name = ''
        package = Package()
        try:
            with open(packagesFile, errors='replace') as ifile:
                for line in ifile:
                    line = line.rstrip('\r\n')
                    if line.startswith('Package: '):
                        name = line.replace('Package: ', '')
                    elif line.startswith('Depends: '):
                        depends = []
                        for i in line.replace('Depends: ', '').split(', '):
                            depends.append(i.split()[0])
                        package.setDepends(depends)
                    elif line.startswith('Filename: '):
                        package.setUrl(line[10:])
                        packages[name] = package
                        package = Package()
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + packagesFile + '" packages file.')
        return packages

    def _readDistributionPinPackages(self, pinFile):
        packagesCache = {}
        try:
            with open(pinFile, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    if len(columns) != 0:
                        pattern = columns[0]
                        if pattern[:1] != '#':
                            file = os.path.join(os.path.dirname(pinFile), columns[1]) + '.packages'
                            if file not in packagesCache:
                                packagesCache[file] = self._readDistributionPackages(file)
                            try:
                                ispattern = re.compile(
                                    pattern.replace('?', '.').replace('*', '.*')+'$')
                            except sre_constants.error:
                                continue
                            for key, value in packagesCache[file].items():
                                if ispattern.match(key):
                                    self._packages[key] = copy.copy(packagesCache[file][key])
        except IOError:
            pass

    def _readDistributionInstalled(self, installedFile):
        try:
            with open(installedFile, errors='replace') as ifile:
                for line in ifile:
                    columns = line.split()
                    name = columns[0]
                    if name[:1] != '#':
                        if name in self._packages:
                            self._packages[name].setInstalledFlag(True)
        except IOError:
            return

    def _checkPackageInstall(self, distribution, ofile, indent, name):
        if name in self._packages:
            self._packages[name].setCheckedFlag(True)
            if self._packages[name].getInstalledFlag():
                print(indent + self._packages[name].getUrl(), '[Installed]')
            else:
                file = self._local(distribution, self._packages[name].getUrl())
                print(indent + file)
                print(indent + file, file=ofile)
            for i in self._packages[name].getDepends():
                if i in self._packages:
                    if self._packages[i].getInstalledFlag():
                        print(indent + '  ' + self._packages[i].getUrl(), '[Installed]')
                    elif self._packages[i].getCheckedFlag():
                        print(indent + '  ' + self._packages[i].getUrl())
                    elif not self._packages[name].getInstalledFlag():
                        self._checkPackageInstall(distribution, ofile, indent + '  ', i)

    def _checkDistributionInstall(self, distribution, listFile, names):
        urlfile = os.path.basename(distribution) + listFile.split('.debs')[-1] + '.url'
        try:
            with open(urlfile, 'w', newline='\n') as ofile:
                indent = ''
                for i in names:
                    self._checkPackageInstall(distribution, ofile, indent, i)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + urlfile + '" file.')
        if os.path.getsize(urlfile) == 0:
            os.remove(urlfile)

    def _local(self, distribution, url):
        file = os.path.join(distribution, os.path.basename(url))
        if os.path.isfile(file):
            return 'file://' + os.path.abspath(file)
        return url


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            CheckInstall(options)
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
