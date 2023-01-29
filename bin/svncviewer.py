#!/usr/bin/env python3
"""
Sandbox for securely connecting to VNC server using SSH protocol.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import network_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_vncviewer(self) -> network_mod.Sandbox:
        """
        Return vncviewer Command class object.
        """
        return self._vncviewer

    def _getport(self, remote_host: str, remote_port: str) -> str:
        command = command_mod.Command('ss', args=['-lpnt'], errors='ignore')
        pattern = '[::1]:5901 '
        if not command.is_found():
            command = command_mod.Command(
                'lsof',
                args=['-i', 'tcp:5901-5999'],
                errors='ignore'
            )
            pattern = ''
            if not command.is_found():
                command = command_mod.Command('ss', errors='stop')

        task = subtask_mod.Batch(command.get_cmdline())
        task.run(pattern=pattern)
        for local_port in range(5901, 6000):
            if not task.is_match_output(f':{local_port}[ -]'):
                ssh = command_mod.Command('ssh', errors='stop')
                if self._args.ssh_port:
                    ssh.extend_args(['-p', self._args.ssh_port[0]])
                ssh.extend_args([
                    '-f',
                    '-L',
                    f'{local_port}:localhost:{remote_port}',
                    remote_host,
                    'sleep',
                    '64'
                ])
                print(
                    f'Starting "ssh" port forwarding from "localhost:'
                    f'{local_port}" to "{remote_host}:{remote_port}"...',
                )
                subtask_mod.Task(ssh.get_cmdline()).run()
                return str(local_port)
        raise SystemExit(
            f'{sys.argv[0]}: Cannot find unused local port in range 5901-5999.'
        )

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Securely connect to VNC server using SSH protocol.",
        )

        parser.add_argument(
            '-p',
            nargs=1,
            dest='ssh_port',
            default=None,
            metavar='ssh_port',
            help="Select non-default ssh port.",
        )

        parser.add_argument(
            'server',
            nargs=1,
            metavar='[[user]@host]:vnc_port',
            help="VNC server location.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        try:
            remote_host, remote_port = self._args.server[0].split(':')
        except ValueError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'single ":" in VNC server location.',
            ) from exception

        try:
            if int(remote_port) < 101:
                remote_port = str(int(remote_port) + 5900)
        except ValueError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer '
                'for port number.',
            ) from exception

        self._vncviewer = network_mod.Sandbox('vncviewer', errors='stop')
        configs = [
            Path(Path.home(), '.config/ibus'),
            Path(Path.home(), '.vnc'),
        ]
        self._vncviewer.sandbox(configs)

        if remote_host:
            local_port = self._getport(remote_host, remote_port)
            print(
                f'Starting "vncviewer" connection via "localhost:{local_port}"'
                f' to "{remote_host}:{remote_port}"...',
            )
        else:
            local_port = remote_port
            print(
                'Starting "vncviewer" connection to '
                f'"localhost:{local_port}"...',
            )
        self._vncviewer.set_args([f':{local_port}'])


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

        subtask_mod.Daemon(options.get_vncviewer().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
