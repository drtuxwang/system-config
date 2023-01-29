#!/usr/bin/env python3
"""
Create SSH keys and setup access to remote systems.

Generate manually:
ssh-keygen -t rsa -b 4096 -f id_rsa
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_logins(self) -> List[str]:
        """
        Return list of logins.
        """
        return self._args.logins

    def get_ssh(self) -> command_mod.Command:
        """
        Return ssh Command class object.
        """
        return self._ssh

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Create SSH keys and setup access to remote systems.",
        )

        parser.add_argument(
            'logins',
            nargs='+',
            metavar='[user]@host',
            help="Remote login.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._ssh = command_mod.Command('ssh', errors='stop')


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

    def _check(self, options: Options) -> None:
        config = []
        path = Path(self._sshdir, 'config')
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    config.append(line.strip())
        except OSError:
            pass

        for login in options.get_logins():
            if '@' in login:
                ruser = login.split('@')[0]
                rhost = login.split('@')[1]
                if f'Host {rhost}' not in config:
                    print(f'Adding "{login}" to "$HOME/.ssh/config"...')
                    config.extend(['', f'Host {rhost}', f'User {ruser}'])
                    path_new = Path(f'{path}.part')
                    try:
                        with path_new.open('w') as ofile:
                            for line in config:
                                print(line, file=ofile)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create '
                            f'"{path_new}" temporary file.',
                        ) from exception
                    try:
                        path_new.replace(path)
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot update '
                            f'"{path}" configuration file.',
                        ) from exception
            print(f'Checking ssh configuration on "{login}"...')
            stdin = (
                'umask 077; chmod -R go= $HOME/.ssh 2> /dev/null',
                f'PUBKEY="{self._pubkey}"',
                'mkdir $HOME/.ssh 2> /dev/null',
                'if [ ! "`grep \"^$PUBKEY$\" '
                '$HOME/.ssh/authorized_keys 2> /dev/null`" ]',
                'then',
                f'    echo "Adding public key to '
                f'\"{login}:$HOME/.ssh/authorized_keys\"..."',
                '    echo "$PUBKEY" >> $HOME/.ssh/authorized_keys',
                'fi')
            self._ssh.set_args([login, '/bin/sh'])
            task = subtask_mod.Task(self._ssh.get_cmdline())
            task.run(stdin=stdin)
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    def _add_authorized_key(self, pubkey: str) -> None:
        path = Path(self._sshdir, 'authorized_keys')
        pubkeys: List[str] = []
        if path.is_file():
            try:
                with path.open(errors='replace') as ifile:
                    pubkeys = []
                    for line in ifile:
                        pubkeys.append(line.strip())
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{path}" authorised key file.'
                ) from exception

        path_new = Path(f'{path}.part')
        if pubkey not in pubkeys:
            try:
                with path_new.open('w') as ofile:
                    for line in pubkeys:
                        print(line, file=ofile)
                    print(pubkey, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{path_new}" temporary file.',
                ) from exception
            try:
                path_new.replace(path)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot update '
                    f'"{path}" authorised key file.',
                ) from exception

    def _config(self) -> str:
        os.umask(0o077)
        if self._sshdir.is_dir():
            for file in Path(Path.home(), '.ssh').glob('*'):
                try:
                    file.chmod(0o700)
                except OSError:
                    pass
        else:
            try:
                self._sshdir.mkdir()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{self._sshdir}" configuration directory.',
                ) from exception

        private_key = Path(self._sshdir, 'id_rsa')
        if not private_key.is_file():
            print("\nGenerating 4096bit RSA private/public key pair...")
            ssh_keygen = command_mod.Command('ssh-keygen', errors='stop')
            ssh_keygen.set_args([
                '-t',
                'rsa',
                '-b',
                '4096',
                '-f',
                str(private_key),
                '-N',
                '',
            ])
            task = subtask_mod.Task(ssh_keygen.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            ssh_add = command_mod.Command('ssh-add', errors='ignore')
            if ssh_add.is_found():
                # When SSH_AUTH_SOCK agent is used
                subtask_mod.Batch(ssh_add.get_cmdline()).run()

        path = Path(self._sshdir, 'id_rsa.pub')
        try:
            with path.open(errors='replace') as ifile:
                pubkey = ifile.readline().strip()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" public key file.'
            ) from exception

        if pubkey:
            self._add_authorized_key(pubkey)

        return pubkey

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._ssh = options.get_ssh()

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine HOME directory.",
            )
        self._sshdir = Path(Path.home(), '.ssh')
        self._pubkey = self._config()
        self._check(options)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
