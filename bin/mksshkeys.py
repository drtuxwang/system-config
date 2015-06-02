#!/usr/bin/env python3
"""
Create SSH keys and setup access to remote systems.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self._ssh = syslib.Command("ssh")


    def getLogins(self):
        """
        Return list of logins.
        """
        return self._args.logins


    def getSsh(self):
        """
        Return ssh Command class object.
        """
        return self._ssh

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Create SSH keys and setup access to remote systems.")

        parser.add_argument("logins", nargs="+", metavar="[user]@host",
                            help="Remote login.")

        self._args = parser.parse_args(args)


class SecureShell(syslib.Dump):


    def __init__(self, options):
        self._ssh = options.getSsh()

        if "HOME" not in os.environ.keys():
            raise SystemExit(sys.argv[0] + ": Cannot determine HOME directory.")
        self._sshdir = os.path.join(os.environ["HOME"], ".ssh")
        self._pubkey = self._config()
        self._check(options)


    def _check(self, options):
        configfile = os.path.join(self._sshdir, "config")
        try:
            with open(configfile, errors="replace") as ifile:
                config = []
                for line in ifile:
                    config.append(line.strip())
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + configfile + '" configuation file.')

        for login in options.getLogins():
            if "@" in login:
                ruser = login.split("@")[0]
                rhost = login.split("@")[1]
                if "Host " + rhost not in config:
                    print('Adding "' + login + '" to "$HOME/.ssh/config"...')
                    config.extend([ "", "Host " + rhost, "User " + ruser ])
                    try:
                        with open(configfile + "-new", "w", newline = "\n") as ofile:
                            for line in config:
                                print(line, file=ofile)
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                         configfile + "-new" + '" temporary file.')
                    try:
                        os.rename(configfile + "-new", configfile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot update "' +
                                         configfile + '" configuration file.')
            print('Checking ssh configuration on "' + login + '"...')
            stdin = (
                "umask 077; chmod -R go= $HOME/.ssh 2> /dev/null",
                'PUBKEY="' + self._pubkey + '"',
                "mkdir $HOME/.ssh 2> /dev/null",
                'if [ ! r"`grep \"^$PUBKEY$\" $HOME/.ssh/authorized_keys" " 2> /dev/null`" ]; then',
                '  echo "Adding public key to \"' + login + ':$HOME/.ssh/authorized_keys\"..."',
                '  echo "$PUBKEY" >> $HOME/.ssh/authorized_keys',
                "fi")
            self._ssh.setArgs([ login, "/bin/sh" ])
            self._ssh.run(stdin=stdin)
            if self._ssh.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ssh.getExitcode()) +
                                 ' received from "' + self._ssh.getFile() + '".')


    def _config(self):
        os.umask(int("077", 8))
        if os.path.isdir(self._sshdir):
            for file in glob.glob(os.path.join(os.environ["HOME"], ".ssh", "*")):
                try:
                    os.chmod(file, int("700", 8))
                except OSError:
                    pass
        else:
            try:
                os.mkdir(self._sshdir)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + self._sshdir +
                                 '" configuration directory.')

        privateKey = os.path.join(self._sshdir, "id_rsa")
        if not os.path.isfile(privateKey):
            print("\nGenerating 2048bit RSA private/public key pair...")
            ssh_keygen = syslib.Command("ssh-keygen")
            ssh_keygen.setArgs([ "-t", "rsa", "-b", "2048", "-f", privateKey, "-N", "" ])
            ssh_keygen.run()
            if ssh_keygen.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(ssh_keygen.getExitcode()) +
                                 ' received from "' + ssh_keygen.getFile() + '".')
            sshAdd = syslib.Command("ssh-add", check=False)
            if sshAdd.isFound():
                # When SSH_AUTH_SOCK agent is used
                sshAdd.run(mode="batch")
        try:
            with open(os.path.join(self._sshdir, "id_rsa.pub"), errors="replace") as ifile:
                pubkey = ifile.readline().strip()
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' +
                    os.path.join(self._sshdir, "id_rsa.pub") + '" public key file.')

        if pubkey:
            file = os.path.join(self._sshdir, "authorized_keys")
            pubkeys = []
            if os.path.isfile(file):
                try:
                    with open(file, errors="replace") as ifile:
                        pubkeys = []
                        for line in ifile:
                            pubkeys.append(line.strip())
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' +
                                     file + '" authorised key file.')
            if pubkey not in pubkeys:
                try:
                    with open(file + "-new", "w", newline="\n") as ofile:
                        for line in pubkeys:
                            print(line, file=ofile)
                        print(pubkey, file=ofile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                     file + "-new" + '" temporary file.')
                try:
                    os.rename(file + "-new", file)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot update "' +
                                     file + '" authorised key file.')
            if not os.path.isfile(file + "2"):
                # Older systems uses "$HOME/.ssh/authorized_keys2"
                try:
                    os.symlink("authorized_keys", file + "2")
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '2" link.')

        privateKeyDsa = os.path.join(self._sshdir, "id_dsa")
        if not os.path.islink(privateKeyDsa):
            if os.path.isfile(privateKeyDsa):
                try:
                    os.remove(privateKeyDsa)
                    os.remove(privateKeyDsa + ".pub")
                except OSError:
                    pass
            try:
                os.symlink("id_rsa", privateKeyDsa) # DSA keys are insecure
            except OSError:
                pass
        configfile = os.path.join(self._sshdir, "config")
        if not os.path.isfile(configfile):
            print('Creating "$HOME/.ssh/config"...')
            try:
                with open(configfile, "w", newline="\n") as ofile:
                    print("Protocol 2", file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 configfile + '" configuation file.')
        return pubkey


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            SecureShell(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
