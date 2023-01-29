#!/usr/bin/env python3
"""
Wrapper for "chroot" command
"""

import getpass
import os
import signal
import socket
import sys
from pathlib import Path
from typing import Any, List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_directory(self) -> Path:
        """
        Return directory.
        """
        return self._path

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if len(args) != 2 or not Path(args[1]).is_dir():
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
            sudo.set_args([
                '-p',
                prompt,
                'python3',
                __file__,
                Path(args[1]).resolve(),
            ])
            subtask_mod.Exec(sudo.get_cmdline()).run()
        if not Path(args[1], 'bin', 'bash').is_file():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "/bin/bash" in chroot directory.',
            )
        self._path = Path(args[1]).resolve()


class Chroot:
    """
    Change root class
    """

    def __init__(self, path: Path) -> None:
        self._chroot = command_mod.Command('/usr/sbin/chroot', errors='stop')
        self._chroot.set_args([path, '/usr/bin/env', 'bash', '-l'])
        self._path = path
        self._mount = command_mod.Command('mount', errors='stop')

        self._mountpoints: List[str] = []
        self.mount_dir(
            '-o',
            'bind',
            '/dev',
            Path(path, 'dev'),
        )
        self.mount_dir(
            '-o',
            'bind',
            '/proc',
            Path(path, 'proc'),
        )
        if (
            Path('/shared').is_dir() and
            Path(path, 'shared').is_dir()
        ):
            self.mount_dir(
                '-o',
                'bind',
                '/shared',
                Path(path, 'shared'),
            )
        self.mount_dir(
            '-t',
            'tmpfs',
            '-o',
            'size=256m,noatime,nosuid,nodev',
            'tmpfs',
            Path(path, 'tmp'),
        )
        if (
            Path('/var/run/dbus').is_dir() and
            Path(path, 'var/run/dbus').is_dir()
        ):
            self.mount_dir(
                '-o',
                'bind', '/var/run/dbus',
                Path(path, 'var/run/dbus'),
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
        print(f'Chroot "{self._path}" starting...')
        subtask_mod.Task(self._chroot.get_cmdline()).run()
        umount = command_mod.Command(
            'umount',
            args=['-l'] + self._mountpoints,
            errors='stop'
        )
        subtask_mod.Task(umount.get_cmdline()).run()
        print(f'Chroot "{self._path}" finished!')


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
