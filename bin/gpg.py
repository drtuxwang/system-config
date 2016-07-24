#!/usr/bin/env python3
"""
Make an encrypted archive in gpg (pgp compatible) format.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def _config_encoder(self):
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
            file = self._args.file
            if os.path.isfile(file):
                if file.endswith('.gpg') or file.endswith('.pgp'):
                    self._gpg.set_args([file])
                else:
                    if self._args.recipent:
                        self._gpg.extend_args(
                            ['--recipient', self._args.recipent])
                    self._gpg.extend_args(
                        ['--output=' + file + extension, '--encrypt', file])
            else:
                self._gpg.set_args(file)

    @staticmethod
    def _config():
        if 'HOME' in os.environ:
            os.umask(int('077', 8))
            gpgdir = os.path.join(os.environ['HOME'], '.gnupg')
            if not os.path.isdir(gpgdir):
                try:
                    os.mkdir(gpgdir)
                except OSError:
                    return
            try:
                os.chmod(gpgdir, int('700', 8))
            except OSError:
                return

    @staticmethod
    def _set_libraries(command):
        libdir = os.path.join(os.path.dirname(command.get_file()), 'lib')
        if os.path.isdir(libdir) and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    def get_gpg(self):
        """
        Return gpg Command class object.
        """
        return self._gpg

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make an encrypted archive in gpg '
            '(pgp compatible) format.'
        )

        parser.add_argument(
            '-a',
            dest='ascii_flag',
            action='store_true',
            help='Select ASCII text encrypted output.'
        )
        parser.add_argument(
            '-r',
            nargs=1,
            dest='recipient',
            help='Recipient for encryption.'
        )
        parser.add_argument(
            '-add',
            nargs=1,
            metavar='file.pub',
            help='Add public key.'
        )
        parser.add_argument(
            '-mkkey',
            action='store_true',
            dest='make_flag',
            help='Generate a new pair of public/private keys.'
        )
        parser.add_argument(
            '-passwd',
            nargs=1,
            metavar='keyid',
            help='Generate a new pair of public/private keys.'
        )
        parser.add_argument(
            '-pub',
            nargs=1,
            metavar='keyid',
            help='Extract public key.'
        )
        parser.add_argument(
            '-sign',
            action='store_true',
            dest='sign_flag',
            help='Sign file to prove your identity.'
        )
        parser.add_argument(
            '-trust',
            nargs=1,
            metavar='keyid',
            help='Trust identity of public key owner.'
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show all public/private keys in keyring.'
        )
        parser.add_argument(
            'file',
            nargs='?',
            help='File to encrypt/decrypt.'
        )
        parser.add_argument(
            'recipent',
            nargs='?',
            help='Recipient name or ID.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._config()

        self._gpg = command_mod.Command('gpg', errors='stop')
        self._set_libraries(self._gpg)

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
            self._gpg.extend_args(
                ['--edit-key', self._args.passwd[0], 'passwd'])

        elif self._args.pub:
            self._gpg.extend_args(
                ['--openpgp', '--export', '--armor', self._args.pub[0]])

        elif self._args.trust:
            self._gpg.extend_args(['--sign-key', self._args.trust[0]])

        elif self._args.view_flag:
            self._gpg.extend_args(['--list-keys'])
            task = subtask_mod.Task(self._gpg.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            self._gpg.set_args(['--list-secret-keys'])

        else:
            self._config_encoder()


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Exec(options.get_gpg().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
