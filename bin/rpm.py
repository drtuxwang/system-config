#!/usr/bin/env python3
"""
Wrapper for "rpm" command (adds 'rpm -l')
"""

import glob
import os
import shutil
import signal
import sys
from typing import List

import command_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_mode(self) -> str:
        """
        Return operation mode.
        """
        return self._mode

    def get_rpm(self) -> command_mod.Command:
        """
        Return rpm Command class object.
        """
        return self._rpm

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._rpm = command_mod.Command('rpm', errors='stop')
        if len(args) == 1 or args[1] != '-l':
            self._rpm.set_args(sys.argv[1:])
            subtask_mod.Exec(self._rpm.get_cmdline()).run()

        self._mode = 'show_packages_info'


class Package:
    """
    Package class
    """

    def __init__(self, version: str, size: int, description: str) -> None:
        self._version = version
        self._size = size
        self._description = description

    def get_description(self) -> str:
        """
        Return package description.
        """
        return self._description

    def set_description(self, description: str) -> None:
        """
        Set package description.

        description = Package description
        """
        self._description = description

    def get_size(self) -> int:
        """
        Return package size.
        """
        return self._size

    def set_size(self, size: int) -> None:
        """
        Set package size.

        size = Package size
        """
        self._size = size

    def get_version(self) -> str:
        """
        Return package version.
        """
        return self._version

    def set_version(self, version: str) -> None:
        """
        Set package version.

        version = Package version
        """
        self._version = version


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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

        # Send ".rpmdb" to tmpfs
        tmpdir = file_mod.FileUtil.tmpdir(os.path.join('.cache', 'rpmdb'))
        directory = os.path.join(os.environ.get('HOME'), '.rpmdb')
        if not os.path.islink(directory):
            try:
                shutil.rmtree(directory)
            except OSError:
                pass
            try:
                os.symlink(tmpdir, directory)
            except OSError:
                pass

    @staticmethod
    def _read_rpm_status(options: Options) -> dict:
        rpm = options.get_rpm()
        rpm.set_args(['-a', '-q', '-i'])
        task = subtask_mod.Batch(rpm.get_cmdline())
        task.run()
        name = ''
        packages = {}
        package = Package('', -1, '')

        for line in task.get_output():
            if line.startswith('Name '):
                name = line.split()[2]
            elif line.startswith('Version '):
                package.set_version(line.split()[2])
            elif line.startswith('Size '):
                try:
                    package.set_size(int((int(line.split()[2]) + 1023) / 1024))
                except ValueError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Package '
                        f'"{name}" has non integer size.',
                    ) from exception
            elif line.startswith('Summary '):
                package.set_description(line.split(': ')[1])
                packages[name] = package
                package = Package('', 0, '')
        return packages

    @staticmethod
    def _show_packages_info(packages: dict) -> None:
        for name, package in sorted(packages.items()):
            print(
                f"{name.split(':')[0]:35s} "
                f"{package.get_version():15s} "
                f"{package.get_size():5d}KB "
                f"{package.get_description()}",
            )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        packages = self._read_rpm_status(options)
        self._show_packages_info(packages)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
