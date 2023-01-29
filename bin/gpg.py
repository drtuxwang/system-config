#!/usr/bin/env python3
"""
Make an encrypted archive in gpg (pgp compatible) format.
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
        self._config()
        self.parse(sys.argv)

    def _config_encoder(self) -> None:
        extension = '.gpg'
        if self._args.ascii_flag:
            self._gpg.append_arg('--armor')
            extension = '.asc'
        if self._args.recipient:
            self._gpg.extend_args(
                ['--batch', '--recipient', self._args.recipient[0]])
        if self._args.sign_flag:
            self._gpg.append_arg('--sign')

        if self._args.file:
            path = Path(self._args.file)
            if path.is_file():
                if path.suffix in ('.gpg', '.pgp'):
                    self._gpg.set_args([path])
                else:
                    if self._args.recipent:
                        self._gpg.extend_args(
                            ['--recipient', self._args.recipent]
                        )
                    self._gpg.extend_args([
                        f'--output={path}{extension}',
                        '--encrypt',
                        str(path),
                    ])
            else:
                self._gpg.set_args([path])

    @staticmethod
    def _config() -> None:
        os.umask(0o077)
        gpgdir = Path(Path.home(), '.gnupg')
        if not gpgdir.is_dir():
            try:
                gpgdir.mkdir()
            except OSError:
                return
        if 'DISPLAY' in os.environ:
            del os.environ['DISPLAY']

    def get_gpg(self) -> command_mod.Command:
        """
        Return gpg Command class object.
        """
        return self._gpg

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Make an encrypted archive in gpg "
            "(pgp compatible) format.",
        )

        parser.add_argument(
            '-a',
            dest='ascii_flag',
            action='store_true',
            help="Select ASCII text encrypted output.",
        )
        parser.add_argument(
            '-r',
            nargs=1,
            dest='recipient',
            help="Recipient for encryption.",
        )
        parser.add_argument(
            '-add',
            nargs=1,
            metavar='file.pub',
            help="Add public key.",
        )
        parser.add_argument(
            '-mkkey',
            action='store_true',
            dest='make_flag',
            help="Generate a new pair of public/private keys.",
        )
        parser.add_argument(
            '-passwd',
            nargs=1,
            metavar='keyid',
            help="Set private key passphrase.",
        )
        parser.add_argument(
            '-pub',
            nargs=1,
            metavar='keyid',
            help="Extract public key.",
        )
        parser.add_argument(
            '-sign',
            action='store_true',
            dest='sign_flag',
            help="Sign file to prove your identity.",
        )
        parser.add_argument(
            '-trust',
            nargs=1,
            metavar='keyid',
            help="Trust identity of public key owner.",
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show all public/private keys in keyring.",
        )
        parser.add_argument(
            'file',
            nargs='?',
            help="File to encrypt/decrypt.",
        )
        parser.add_argument(
            'recipent',
            nargs='?',
            help="Recipient name or ID.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._config()

        self._gpg = command_mod.Command('gpg2', errors='ignore')
        if not self._gpg.is_found():
            self._gpg = command_mod.Command('gpg', errors='stop')

        if len(args) > 1 and args[1].startswith('--'):
            self._gpg.set_args(args[1:])
            subtask_mod.Exec(self._gpg.get_cmdline()).run()

        self._parse_args(args[1:])

        self._gpg.set_args(['--openpgp', '-z', '0'])

        if self._args.add:
            self._gpg.extend_args(['--import', self._args.add[0]])
        elif self._args.make_flag:
            self._gpg.extend_args(['--gen-key'])
        elif self._args.passwd:
            self._gpg.extend_args([
                '--edit-key',
                self._args.passwd[0],
                'passwd',
            ])
        elif self._args.pub:
            self._gpg.extend_args([
                '--openpgp',
                '--export',
                '--armor',
                self._args.pub[0],
            ])
        elif self._args.trust:
            self._gpg.extend_args(['--sign-key', self._args.trust[0]])
        elif self._args.view_flag:
            self._gpg.extend_args(['--list-keys'])
            task = subtask_mod.Task(self._gpg.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            self._gpg.set_args(['--list-secret-keys'])
        else:
            self._config_encoder()


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

        task = subtask_mod.Task(options.get_gpg().get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

        path = Path(task.get_cmdline()[-1])
        if path.is_file() and len(task.get_cmdline()) > 3:
            path_new = Path(task.get_cmdline()[-3].split('--output=')[-1])
            if path_new.is_file():
                file_time = int(path.stat().st_mtime)
                os.utime(path_new, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
