#!/usr/bin/env python3
"""
Make an encrypted archive in gpg (pgp compatible) format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._config()

        self._gpg = syslib.Command('gpg')
        self._setLibraries(self._gpg)

        if len(args) > 1 and args[1].startswith('--'):
            self._gpg.setArgs(args[1:])
            self._gpg.run(mode='exec')

        self._parseArgs(args[1:])

        self._gpg.setFlags(['--openpgp', '-z', '0'])

        if self._args.add:
            self._gpg.setArgs(['--import', self._args.add[0]])

        elif self._args.makeFlag:
            self._gpg.setArgs(['--gen-key'])

        elif self._args.passwd:
            self._gpg.setArgs(['--edit-key', self._args.passwd[0], 'passwd'])

        elif self._args.pub:
            self._gpg.setArgs(['--openpgp', '--export', '--armor', self._args.pub[0]])

        elif self._args.trust:
            self._gpg.setArgs(['--sign-key', self._args.trust[0]])

        elif self._args.viewFlag:
            self._gpg.setArgs(['--list-keys'])
            self._gpg.run()
            if self._gpg.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._gpg.getExitcode()) +
                                 ' received from "' + self._gpg.getFile() + '".')
            self._gpg.setArgs(['--list-secret-keys'])

        else:
            extension = '.gpg'
            if self._args.asciiFlag:
                self._gpg.appendArg('--armor')
                extension = '.asc'
            if self._args.recipient:
                self._gpg.extendArgs(['--batch', '--recipient', self._args.recipient[0]])
            if self._args.signFlag:
                self._gpg.appendArg('--sign')

            if self._args.file:
                file = self._args.file
                if os.path.isfile(file):
                    if file.endswith('.gpg') or file.endswith('.pgp'):
                        self._gpg.setArgs([file])
                    else:
                        if self._args.recipent:
                            self._gpg.extendArgs(['--recipient', self._args.recipent])
                        self._gpg.extendArgs(['--output=' + file + extension, '--encrypt', file])
                else:
                    self._gpg.setArgs(file)

    def _config(self):
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

    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), 'lib')
        if os.path.isdir(libdir):
            if syslib.info.getSystem() == 'linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    def getGpg(self):
        """
        Return gpg Command class object.
        """
        return self._gpg

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Make an encrypted archive in gpg (pgp compatible) format.')

        parser.add_argument('-a', dest='asciiFlag', action='store_true',
                            help='Select ASCII text encrypted output.')
        parser.add_argument('-r', nargs=1, dest='recipient', help='Recipient for encryption.')
        parser.add_argument('-add', nargs=1, metavar='file.pub', help='Add public key.')
        parser.add_argument('-mkkey', action='store_true', dest='makeFlag',
                            help='Generate a new pair of public/private keys.')
        parser.add_argument('-passwd', nargs=1, metavar='keyid',
                            help='Generate a new pair of public/private keys.')
        parser.add_argument('-pub', nargs=1, metavar='keyid',
                            help='Extract public key.')
        parser.add_argument('-sign', action='store_true', dest='signFlag',
                            help='Sign file to prove your identity.')
        parser.add_argument('-trust', nargs=1, metavar='keyid',
                            help='Trust identity of public key owner.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show all public/private keys in keyring.')

        parser.add_argument('file', nargs='?', help='File to encrypt/decrypt.')
        parser.add_argument('recipent', nargs='?', help='Recipient name or ID.')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getGpg().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
