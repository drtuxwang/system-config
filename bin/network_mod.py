#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2021 By Dr Colin Kong
"""

import grp
import json
import os
import sys
from typing import Any, List, Optional

import command_mod

RELEASE = '3.2.1'
VERSION = 20210731


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

    def __init__(self, program: str, **kwargs: Any) -> None:
        super().__init__(program, **kwargs)
        self._sandbox: List[str] = []

    @staticmethod
    def _check_nonet(errors: str) -> bool:
        user = os.getlogin()
        for name, _, _, members in grp.getgrall():
            if name == 'nonet':
                if user in members:
                    return True
                break

        if errors == 'stop':
            raise SystemExit(
                sys.argv[0] + ': User "' + user +
                '" is not member of "nonet" group.'
            )
        return False

    def sandbox(
        self,
        nonet: bool = False,
        writes: Optional[List[str]] = None,
        errors: str = 'ignore',
    ) -> None:
        """
        Setup sandboxing

        nonet  = Disable external network access
        writes = Restrict disk writes to directory list
        errors = Optional error handling ('stop' or 'ignore')
        """
        if not nonet and not writes:
            return
        command = command_mod.Command('bwrap', errors=errors)
        if not command.is_found():
            return

        cmdline = command.get_cmdline()
        if writes:
            cmdline.extend(['--ro-bind', '/', '/', '--tmpfs', '/tmp'])
            home = os.getenv('HOME')
            if home:
                cmdline.extend(['--tmpfs', home])
                for directory in ('.bashrc', '.profile'):
                    path = os.path.join(home, directory)
                    realpath = os.path.realpath(path)
                    cmdline.extend(['--ro-bind-try', realpath, path])
            for directory in writes:
                realpath = os.path.realpath(directory)
                cmdline.extend(['--bind', realpath, directory])
        else:
            cmdline.extend(['--bind', '/', '/'])
        cmdline.extend(['--dev', '/dev', '--'])

        if nonet and self._check_nonet(errors):
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
