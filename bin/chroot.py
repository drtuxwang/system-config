#!/usr/bin/env python3
"""
Wrapper for "chroot" command
"""

import getpass
import glob
import os
import signal
import socket
import sys
from typing import Any, List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_directory(self) -> str:
        """
        Return directory.
        """
        return self._directory

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if len(args) != 2 or not os.path.isdir(args[1]):
            chroot = command_mod.Command(
                'chroot',
                args=args[1:],
                errors='stop'
            )
            subtask_mod.Exec(chroot.get_cmdline()).run()
        elif getpass.getuser() != 'root':
            hostname = socket.gethostname().split('.')[0].lower()
            username = getpass.getuser()
            prompt = f'[sudo] password for {hostname}@{username}: '
            sudo = command_mod.Command('sudo', errors='stop')
            sudo.set_args(
                ['-p', prompt, 'python3', __file__, os.path.abspath(args[1])])
            subtask_mod.Exec(sudo.get_cmdline()).run()
        if not os.path.isfile(os.path.join(args[1], 'bin', 'bash')):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "/bin/bash" in chroot directory.',
            )
        self._directory = os.path.abspath(args[1])


class Chroot:
    """
    Change root class
    """

    def __init__(self, directory: str) -> None:
        self._chroot = command_mod.Command('/usr/sbin/chroot', errors='stop')
        self._chroot.set_args([directory, '/usr/bin/env', 'bash', '-l'])
        self._directory = directory
        self._mount = command_mod.Command('mount', errors='stop')

        self._mountpoints: List[str] = []
        self.mount_dir(
            '-o',
            'bind',
            '/dev',
            os.path.join(self._directory, 'dev')
        )
        self.mount_dir(
            '-o',
            'bind',
            '/proc',
            os.path.join(self._directory, 'proc')
        )
        if (os.path.isdir('/shared') and
                os.path.isdir(os.path.join(self._directory, 'shared'))):
            self.mount_dir(
                '-o',
                'bind',
                '/shared',
                os.path.join(self._directory, 'shared')
            )
        self.mount_dir(
            '-t',
            'tmpfs',
            '-o',
            'size=256m,noatime,nosuid,nodev',
            'tmpfs',
            os.path.join(self._directory, 'tmp')
        )
        if (os.path.isdir('/var/run/dbus') and
                os.path.isdir(os.path.join(self._directory, 'var/run/dbus'))):
            self.mount_dir(
                '-o',
                'bind', '/var/run/dbus',
                os.path.join(self._directory, 'var/run/dbus')
            )

    def mount_dir(self, *args: Any) -> None:
        """
        Mount directory
        """
        self._mount.set_args(list(args))
        subtask_mod.Task(self._mount.get_cmdline()).run()
        self._mountpoints.append(args[-1])

    def run(self) -> None:
        """
        Start session
        """
        print(f'Chroot "{self._directory}" starting...')
        subtask_mod.Task(self._chroot.get_cmdline()).run()
        umount = command_mod.Command(
            'umount',
            args=['-l'] + self._mountpoints,
            errors='stop'
        )
        subtask_mod.Task(umount.get_cmdline()).run()
        print(f'Chroot "{self._directory}" finished!')


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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        Chroot(options.get_directory()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
