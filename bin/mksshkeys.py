#!/usr/bin/env python3
"""
Create SSH keys and setup access to remote systems.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_logins(self):
        """
        Return list of logins.
        """
        return self._args.logins

    def get_ssh(self):
        """
        Return ssh Command class object.
        """
        return self._ssh

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create SSH keys and setup access to remote systems.')

        parser.add_argument(
            'logins', nargs='+', metavar='[user]@host', help='Remote login.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._ssh = command_mod.Command('ssh', errors='stop')


class Main:
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

    def _check(self, options):
        config = []
        configfile = os.path.join(self._sshdir, 'config')
        try:
            with open(configfile, errors='replace') as ifile:
                for line in ifile:
                    config.append(line.strip())
        except OSError:
            pass

        for login in options.get_logins():
            if '@' in login:
                ruser = login.split('@')[0]
                rhost = login.split('@')[1]
                if 'Host ' + rhost not in config:
                    print('Adding "' + login + '" to "$HOME/.ssh/config"...')
                    config.extend(['', 'Host ' + rhost, 'User ' + ruser])
                    try:
                        with open(
                            configfile + '-new',
                            'w',
                            newline='\n'
                        ) as ofile:
                            for line in config:
                                print(line, file=ofile)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            configfile + '-new' + '" temporary file.'
                        )
                    try:
                        shutil.move(configfile + '-new', configfile)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot update "' +
                            configfile + '" configuration file.'
                        )
            print('Checking ssh configuration on "' + login + '"...')
            stdin = (
                'umask 077; chmod -R go= $HOME/.ssh 2> /dev/null',
                'PUBKEY="' + self._pubkey + '"',
                'mkdir $HOME/.ssh 2> /dev/null',
                'if [ ! "`grep \"^$PUBKEY$\" '
                '$HOME/.ssh/authorized_keys 2> /dev/null`" ]',
                'then',
                '    echo "Adding public key to \"' + login +
                ':$HOME/.ssh/authorized_keys\"..."',
                '    echo "$PUBKEY" >> $HOME/.ssh/authorized_keys',
                'fi')
            self._ssh.set_args([login, '/bin/sh'])
            task = subtask_mod.Task(self._ssh.get_cmdline())
            task.run(stdin=stdin)
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )

    def _add_authorized_key(self, pubkey):
        file = os.path.join(self._sshdir, 'authorized_keys')
        pubkeys = []
        if os.path.isfile(file):
            try:
                with open(file, errors='replace') as ifile:
                    pubkeys = []
                    for line in ifile:
                        pubkeys.append(line.strip())
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + file +
                    '" authorised key file.'
                )
        if pubkey not in pubkeys:
            try:
                with open(file + '-new', 'w', newline='\n') as ofile:
                    for line in pubkeys:
                        print(line, file=ofile)
                    print(pubkey, file=ofile)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file + '-new' +
                    '" temporary file.'
                )
            try:
                shutil.move(file + '-new', file)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot update "' + file +
                    '" authorised key file.'
                )

    def _config(self):
        os.umask(int('077', 8))
        if os.path.isdir(self._sshdir):
            for file in glob.glob(
                    os.path.join(os.environ['HOME'], '.ssh', '*')
            ):
                try:
                    os.chmod(file, int('700', 8))
                except OSError:
                    pass
        else:
            try:
                os.mkdir(self._sshdir)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + self._sshdir +
                    '" configuration directory.'
                )

        private_key = os.path.join(self._sshdir, 'id_rsa')
        if not os.path.isfile(private_key):
            print("\nGenerating 4096bit RSA private/public key pair...")
            ssh_keygen = command_mod.Command('ssh-keygen', errors='stop')
            ssh_keygen.set_args(
                ['-t', 'rsa', '-b', '4096', '-f', private_key, '-N', ''])
            task = subtask_mod.Task(ssh_keygen.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            ssh_add = command_mod.Command('ssh-add', errors='ignore')
            if ssh_add.is_found():
                # When SSH_AUTH_SOCK agent is used
                subtask_mod.Batch(ssh_add.get_cmdline()).run()

        try:
            with open(
                os.path.join(self._sshdir, 'id_rsa.pub'),
                errors='replace'
            ) as ifile:
                pubkey = ifile.readline().strip()
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' +
                os.path.join(self._sshdir, 'id_rsa.pub') + '" public key file.'
            )

        if pubkey:
            self._add_authorized_key(pubkey)

        return pubkey

    def run(self):
        """
        Start program
        """
        options = Options()

        self._ssh = options.get_ssh()

        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine HOME directory.')
        self._sshdir = os.path.join(os.environ['HOME'], '.ssh')
        self._pubkey = self._config()
        self._check(options)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
