#!/usr/bin/env python3
"""
Wrapper for "rpm" command (adds 'rpm -l')
"""

import dataclasses
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileUtil
from subtask_mod import Batch, Exec


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

    def get_rpm(self) -> Command:
        """
        Return rpm Command class object.
        """
        return self._rpm

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._rpm = Command('rpm', errors='stop')
        if len(args) == 1 or args[1] != '-l':
            self._rpm.set_args(sys.argv[1:])
            Exec(self._rpm.get_cmdline()).run()

        self._mode = 'show_packages_info'


@dataclasses.dataclass
class Package:
    """
    Package class
    """
    version: str
    size: int
    description: str


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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _read_rpm_status(options: Options) -> dict:
        rpm = options.get_rpm()
        rpm.set_args(['-a', '-q', '-i'])
        task = Batch(rpm.get_cmdline())
        task.run()
        name = ''
        packages = {}
        package = Package('', -1, '')

        for line in task.get_output():
            if line.startswith('Name '):
                name = line.split()[2]
            elif line.startswith('Version '):
                package.version = line.split()[2]
            elif line.startswith('Size '):
                try:
                    package.size = int((int(line.split()[2]) + 1023) / 1024)
                except ValueError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Package '
                        f'"{name}" has non integer size.',
                    ) from exception
            elif line.startswith('Summary '):
                package.description = line.split(': ')[1]
                packages[name] = package
                package = Package('', 0, '')
        return packages

    @staticmethod
    def _show_packages_info(packages: dict) -> None:
        for name, package in sorted(packages.items()):
            print(
                f"{name.split(':')[0]:35s} "
                f"{package.version:15s} "
                f"{package.size:5d}KB "
                f"{package.description}",
            )

    def run(self) -> int:
        """
        Start program
        """
        # Send ".rpmdb" to tmpfs
        tmpdir = FileUtil.tmpdir(Path('.cache', 'rpmdb'))
        path = Path(Path.home(), '.rpmdb')
        if not path.is_symlink():
            try:
                shutil.rmtree(path)
            except OSError:
                pass
            try:
                path.symlink_to(tmpdir)
            except OSError:
                pass

        options = Options()

        packages = self._read_rpm_status(options)
        self._show_packages_info(packages)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
