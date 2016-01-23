#!/usr/bin/env python3
"""
Wrapper for 'rpm' command (adds 'rpm -l')
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._rpm = syslib.Command('rpm')
        if len(args) == 1 or args[1] != '-l':
            self._rpm.set_args(sys.argv[1:])
            self._rpm.run(mode='exec')

        self._mode = 'show_packages_info'

    def get_mode(self):
        """
        Return operation mode.
        """
        return self._mode

    def get_rpm(self):
        """
        Return rpm Command class object.
        """
        return self._rpm


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
        Return package description.
        """
        return self._description

    def set_description(self, description):
        """
        Set package description.

        description = Package description
        """
        self._description = description

    def get_size(self):
        """
        Return package size.
        """
        return self._size

    def set_size(self, size):
        """
        Set package size.

        size = Package size
        """
        self._size = size

    def get_version(self):
        """
        Return package version.
        """
        return self._version

    def set_version(self, version):
        """
        Set package version.

        version = Package version
        """
        self._version = version


class PackageManger(object):
    """
    Package manager class
    """

    def __init__(self, options):
        self._options = options
        self._read_rpm_status()

        self._show_packages_info()

    def _read_rpm_status(self):
        rpm = self._options.get_rpm()
        rpm.set_args(['-a', '-q', '-i'])
        rpm.run(mode='batch')
        name = ''
        self._packages = {}
        package = Package('', -1, '')

        for line in rpm.get_output():
            if line.startswith('Name '):
                name = line.split()[2]
            elif line.startswith('Version '):
                package.set_version(line.split()[2])
            elif line.startswith('Size '):
                try:
                    package.set_size(int((int(line.split()[2]) + 1023) / 1024))
                except ValueError:
                    raise SystemExit(sys.argv[0] + ': Package "' + name + '" has non integer size.')
            elif line.startswith('Summary '):
                package.set_description(line.split(': ')[1])
                self._packages[name] = package
                package = Package('', '0', '')
        return

    def _show_packages_info(self):
        for name, package in sorted(self._packages.items()):
            print('{0:35s} {1:15s} {2:5d}KB {3:s}'.format(
                name.split(':')[0], package.get_version(), package.get_size(),
                package.get_description()))


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
            PackageManger(options)
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
