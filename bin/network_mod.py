#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2021 By Dr Colin Kong
"""

import getpass
import glob
import grp
import json
import os
from typing import Any, List, Optional, Tuple

import command_mod

RELEASE = '3.3.2'
VERSION = 20210927


class NetNice(command_mod.Command):
    """
    NetNice network traffic shaping command class
    """

    def __init__(self, drate: int = 8000, errors: str = 'ignore') -> None:
        """
        drate = Download rate (default 8000kbps)
        errors = Optional error handling ('stop' or 'ignore')
        """
        self._drate = drate

        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.config', 'netnice.json')
        if not self._read(file):
            self._write(file)

        # Try trickle bandwidth limits
        super().__init__('trickle', errors=errors)
        if self.is_found():
            self.set_args(['-d', str(self._drate), '-s'])

    def _read(self, file: str) -> bool:
        """
        Read configuration file
        """
        if os.path.isfile(file):
            try:
                with open(file) as ifile:
                    data = json.load(ifile)
                    self._drate = data['trickle']['download']
            except (KeyError, OSError, ValueError):
                pass
            else:
                return True

        return False

    def _write(self, file: str) -> None:
        """
        Write configuration file
        """
        data = {
            'trickle': {
                'download': self._drate
            }
        }
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except OSError:
            pass


class Sandbox(command_mod.Command):
    """
    This class stores a command (uses supplied executable)
    Optional sandbox network and disk writes command class

    Requires "nonet" group membership and Firewalling:
    iptables -I OUTPUT 1 -m <username> --gid-owner nonet -j DROP
    iptables -A OUTPUT -m <username> --gid-owner nonet -d 127.0.0.0/8 -j ACCEPT
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    def __init__(self, program: str, **kwargs: Any) -> None:
        super().__init__(program, **kwargs)
        self._sandbox: List[str] = []

    @staticmethod
    def _show(colour: int, message: str) -> None:
        print("\033[1;3{0:d}mSandbox: {1:s}\033[0m".format(colour, message))

    @classmethod
    def _check_bwrap(cls, errors: str) -> Optional[command_mod.Command]:
        bwrap = command_mod.Command('bwrap', errors='ignore')
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
            realpath = os.path.realpath(mount)

        return (realpath, mount, mode)

    def _config_access(
        self,
        bwrap: command_mod.Command,
        configs: Optional[List[str]],
    ) -> List[str]:

        cmdline = bwrap.get_cmdline()

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
            directories = sorted(set(glob.glob('/*')) - set(allow_reads))
            for mount in directories:
                cmdline.extend(['--tmpfs', mount])
            self._show(
                Sandbox.MAGENTA,
                "Disable read access: {0:s}".format(' '.join(directories)),
            )

            # Dummy working directory ("os.getcwd()" returns realpath instead
            directory = os.environ['PWD']
            if not directory.startswith(allow_reads):
                cmdline.extend(['--tmpfs', directory])

            # Devices
            cmdline.extend(['--dev', 'dev'])

            # Application directory
            directory = os.path.dirname(self.get_file())
            if not directory.startswith(allow_reads):
                realpath = os.path.realpath(directory)
                cmdline.extend(['--ro-bind-try', realpath, directory])
                self._show(
                    Sandbox.YELLOW,
                    "Enable access to application {0:s}:ro".format(
                        directory,
                    ),
                )

            # Home directory
            home = os.getenv('HOME', '/')
            mounts = [
                os.path.join(home, x)
                for x in ('.bashrc', '.profile', '.tmux.conf', '.vimrc')
                if os.path.exists(os.path.join(home, x))
            ]
            for mount in mounts:
                realpath = os.path.realpath(mount)
                cmdline.extend(['--ro-bind-try', realpath, mount])
                self._show(
                    Sandbox.YELLOW,
                    "Enable access {0:s}:ro".format(mount),
                )

        # Enable access rights
        for config in configs:
            realpath, mount, mode = self._parse_config(config)
            if mode == 'read/write':
                if not os.path.exists(realpath):
                    os.makedirs(realpath)
                cmdline.extend(['--bind-try', realpath, mount])
                if realpath == '/':
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
                        "Enable access {0:s}".format(config),
                    )
            elif config.startswith('/dev/'):
                cmdline.extend(['--dev-bind-try', realpath, mount])
                self._show(
                    Sandbox.YELLOW,
                    "Enable access {0:s}".format(config),
                )
            elif not mount.startswith(allow_reads):
                cmdline.extend(['--ro-bind-try', realpath, mount])
                self._show(
                    Sandbox.YELLOW,
                    "Enable read access {0:s}".format(config),
                )

        cmdline.extend([
            '--setenv',
            '_SANDBOX_PARENT',
            str(os.getpid()),
            '--',
        ])

        return cmdline

    def sandbox(
        self,
        configs: Optional[List[str]],
        errors: str = 'ignore',
    ) -> None:
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
            command = command_mod.Command('sg', args=['nonet'], errors=errors)
            cmdline = command.get_cmdline() + [
                command_mod.Command.args2cmd(cmdline),
            ]

        self._sandbox = cmdline

    def get_cmdline(self) -> List[str]:
        """
        Return the command line as a list.
        """
        if self._sandbox:
            if self._sandbox[0].endswith('sg'):
                cmdline = self._sandbox[:-1] + [' '.join([
                    self._sandbox[-1],
                    command_mod.Command.args2cmd(self._args),
                ])]
            else:
                cmdline = self._sandbox + self._args
        else:
            cmdline = self._args

        return cmdline


class SandboxFile(command_mod.CommandFile, Sandbox):
    """
    This class stores a command (uses supplied executable location)
    Optional sandbox network and disk writes command class

    Requires "nonet" group membership and Firewalling:
    iptables -I OUTPUT 1 -m <username> --gid-owner nonet -j DROP
    iptables -A OUTPUT -m <username> --gid-owner nonet -d 127.0.0.0/8 -j ACCEPT
    """


if __name__ == '__main__':
    help(__name__)
