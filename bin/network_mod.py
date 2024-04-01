#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2023 By Dr Colin Kong
"""

import getpass
import glob
import grp
import json
import os
from pathlib import Path
from typing import Any, List, Tuple, Union

from command_mod import Command, CommandFile

RELEASE = '3.4.6'
VERSION = 20240329


class NetNice(Command):
    """
    NetNice network traffic shaping command class
    """

    def __init__(self, drate: int = None, errors: str = 'ignore') -> None:
        """
        drate = Download rate
        errors = Optional error handling ('stop' or 'ignore')
        """
        self._drate = None

        path = Path(Path.home(), '.config', 'netnice.json')
        self._read(path)
        if drate:
            self._drate = drate
            if not path.is_file():
                self._write(path)

        # Try trickle bandwidth limits
        super().__init__('trickle', errors=errors)

        if self.is_found():
            self.set_args(['-s'])
            if self._drate:
                self.extend_args(['-d', self._drate / 8])

    def _read(self, path: Path) -> None:
        """
        Read configuration file
        """
        if path.is_file():
            try:
                data = json.loads(path.read_text(errors='replace'))
                self._drate = data['trickle']['download']
            except (KeyError, OSError, ValueError):
                pass

    def _write(self, path: Path) -> None:
        """
        Write configuration file
        """
        data = {
            'trickle': {
                'download': self._drate
            }
        }
        try:
            with path.open('w', newline='\n') as ofile:
                print(json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except OSError:
            pass


class Sandbox(Command):
    """
    This class stores a command (uses supplied executable)
    Optional sandbox network and disk writes command class

    Requires "nonet" group membership and Firewalling:
    iptables -I OUTPUT 1 -m <username> --gid-owner nonet -j DROP
    iptables -A OUTPUT -m <username> --gid-owner nonet -d 127.0.0.0/8 -j ACCEPT
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    def __init__(self, program: Union[str, Path], **kwargs: Any) -> None:
        super().__init__(program, **kwargs)
        self._sandbox: List[str] = []

    @staticmethod
    def _show(colour: int, message: str) -> None:
        print(f"\x1b[1;3{colour}mSandbox: {message}\x1b[0m")

    @classmethod
    def _check_bwrap(cls, errors: str) -> Command:
        bwrap = Command('bwrap', errors='ignore')
        if not bwrap.is_found():
            if errors == 'stop':
                cls._show(
                    Sandbox.RED,
                    "Cannot find bwrap tool for network/disk sandboxing",
                )
                raise SystemExit(1)
            return None

        return bwrap

    @classmethod
    def _check_nonet(cls, errors: str) -> bool:
        username = getpass.getuser()
        for name, _, _, members in grp.getgrall():
            if name == 'nonet':
                if username in members:
                    return True
                break

        if errors == 'stop':
            cls._show(
                Sandbox.RED,
                "Not nonet group member for iptables network filtering"
            )
            raise SystemExit(1)

        return False

    @staticmethod
    def _parse_config(config: str) -> Tuple[str, str, str]:
        if config.endswith(':ro'):
            mode = 'read'
            config = config.rsplit(':', 1)[0]
        elif config.startswith('/dev/'):
            mode = 'device'
        else:
            mode = 'read/write'

        if ':' in config:
            realpath, mount = config.split(':', 1)
        else:
            mount = config
            realpath = str(Path(mount).resolve())

        return (realpath, mount, mode)

    def _config_access(self, bwrap: Command, configs: list) -> List[str]:

        cmdline: list = bwrap.get_cmdline()

        if '/' not in configs:
            # Disable all write access
            cmdline.extend(['--ro-bind', '/', '/'])
            self._show(
                Sandbox.MAGENTA,
                "Disable write access to entire file system",
            )

            # Disable read access
            allow_reads = tuple([
                '/boot',
                '/bin',
                '/dev',
                '/etc',
                '/lib',
                '/lib32',
                '/lib64',
                '/libx32',
                '/lost+found',
                '/opt',
                '/proc',
                '/root',
                '/run',
                '/sbin',
                '/sys',
                '/usr',
                '/var',
            ] + glob.glob('/init*') + glob.glob('/vm*'))
            directories = [
                x
                for x in sorted(set(glob.glob('/*')) - set(allow_reads))
                if Path(x).is_dir()
            ]
            for mount in directories:
                cmdline.extend(['--tmpfs', mount])
            self._show(
                Sandbox.MAGENTA,
                f"Disable read access: {' '.join(directories)}",
            )

            # Dummy working directory ("os.getcwd()" returns realpath instead
            directory = str(Path.cwd())
            if not directory.startswith(allow_reads):
                cmdline.extend(['--tmpfs', directory])
            # Devices
            cmdline.extend(['--dev', 'dev'])

            # Application directory
            path = Path(self.get_file()).parent
            if not str(path).startswith(allow_reads):
                cmdline.extend(['--ro-bind-try', path.resolve(), path])
                self._show(
                    Sandbox.YELLOW,
                    f"Enable application access {path}:ro",
                )

        # Enable access rights
        enabled = []
        for config in [str(x) for x in configs]:
            if config in enabled:
                continue
            enabled.append(config)

            realpath, mount, mode = self._parse_config(config)
            if mode == 'read/write':
                if not Path(realpath).exists():
                    Path(realpath).mkdir(parents=True)
                cmdline.extend(['--bind-try', realpath, mount])
                if str(realpath) == '/':
                    cmdline.extend([
                        '--dev',
                        'dev',
                        '--dev-bind-try',
                        '/dev/dri',
                        '/dev/dri',
                        '--dev-bind-try',
                        '/dev/shm',
                        '/dev/shm',
                    ])
                else:
                    self._show(
                        Sandbox.YELLOW,
                        f"Enable write access {config}",
                    )
            elif config.startswith('/dev/'):
                cmdline.extend(['--dev-bind-try', realpath, mount])
                self._show(
                    Sandbox.YELLOW,
                    f"Enable device access {config}",
                )
            elif not mount.startswith(allow_reads):
                cmdline.extend(['--ro-bind-try', realpath, mount])
                self._show(
                    Sandbox.YELLOW,
                    f"Enable read access {config}",
                )

        cmdline.extend(['--setenv', '_SANDBOX_PARENT', os.getpid(), '--'])

        return cmdline

    def sandbox(self, configs: list, errors: str = 'ignore') -> None:
        """
        Setup sandboxing

        configs = Allow access to file/path/device ([realpath:]file[:ro]|net)
        errors  = Optional error handling ('stop' or 'ignore')
        """
        if os.environ.get('_SANDBOX_PARENT'):
            return
        network = 'net' in configs
        if network:
            configs.remove('net')

        # Check sandbox setup
        bwrap = self._check_bwrap(errors=errors)
        if not bwrap:
            return
        if not network and not self._check_nonet(errors):
            return

        self._show(Sandbox.BLUE, self.get_file())

        if not network:
            self._show(
                Sandbox.MAGENTA,
                "Disable external network access "
                "(using nonet group & iptables)",
            )

        cmdline = self._config_access(bwrap, configs)

        if not network:
            command = Command('sg', args=['nonet'], errors=errors)
            cmdline = command.get_cmdline() + [Command.args2cmd(cmdline)]

        self._sandbox = cmdline

    def get_cmdline(self) -> List[str]:
        """
        Return the command line as a list.
        """
        if self._sandbox:
            if self._sandbox[0].endswith('sg'):
                cmdline = self._sandbox[:-1] + [' '.join([
                    self._sandbox[-1],
                    Command.args2cmd(self._args),
                ])]
            else:
                cmdline = self._sandbox + self._args
        else:
            cmdline = self._args

        return cmdline


class SandboxFile(CommandFile, Sandbox):
    """
    This class stores a command (uses supplied executable location)
    Optional sandbox network and disk writes command class

    Requires "nonet" group membership and Firewalling:
    iptables -I OUTPUT 1 -m <username> --gid-owner nonet -j DROP
    iptables -A OUTPUT -m <username> --gid-owner nonet -d 127.0.0.0/8 -j ACCEPT
    """


if __name__ == '__main__':
    help(__name__)
