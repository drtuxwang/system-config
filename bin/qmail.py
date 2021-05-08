#!/usr/bin/env python3
"""
Quick commandline E-mailer.

"$HOME/.address" stores sender E-mail
"""

import argparse
import getpass
import glob
import os
import re
import signal
import smtplib
import sys
from typing import List

import command_mod
import file_mod
import subtask_mod

RELEASE = '3.1.0'

SOCKET_TIMEOUT = 10


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release = RELEASE
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_addresses(self) -> List[str]:
        """
        Return my addresses.
        """
        return self._args.addresses

    def get_editor(self) -> command_mod.Command:
        """
        Return editor Command class object.
        """
        return self._editor

    def get_my_address(self) -> str:
        """
        Return my address.
        """
        return self._my_address

    def get_release(self) -> str:
        """
        Return release version.
        """
        return self._release

    def get_sendmail(self) -> command_mod.Command:
        """
        Return sendmail Command class object.
        """
        return self._sendmail

    def get_tmpfile(self) -> str:
        """
        Return tmpfile.
        """
        return self._tmpfile

    @staticmethod
    def _address() -> str:
        file = os.path.join(os.environ['HOME'], '.address')
        if os.path.isfile(file):
            try:
                with open(file, errors='replace') as ifile:
                    my_address = ifile.readline().strip()
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + file +
                    '" configuration file.'
                ) from exception
        else:
            my_address = getpass.getuser() + '@localhost'
            print('Creating "' + file + '"...')
            try:
                with open(file, 'w', newline='\n') as ofile:
                    print(my_address, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file +
                    '" configuration file.'
                ) from exception
        return my_address

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Qwikmail v' + self._release +
            ', Quick commandline E-mailer.',
        )

        parser.add_argument(
            'addresses',
            nargs='+',
            metavar='address',
            help='E-mail addresses.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._sendmail = command_mod.Command(
            'sendmail',
            pathextra=['/usr/lib'],
            errors='stop'
        )
        self._sendmail.set_args(['-t'])

        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')
        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        self._tmpfile = os.path.join(tmpdir, 'qmail.tmp' + str(os.getpid()))

        self._editor = command_mod.Command('fedit', errors='ignore')
        if not self._editor.is_found():
            self._editor = command_mod.Command('vi', errors='stop')
        self._editor.set_args([self._tmpfile])

        self._my_address = self._address()


class Mailer:
    """
    E-mail using SMTP servers.
    """

    def __init__(self, host: str) -> None:
        """
        host = SMTP server host
        """
        self._host = host
        self._smtp = None

        try:
            self._smtp = smtplib.SMTP(host, timeout=SOCKET_TIMEOUT)
        except Exception as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot connect to STMP server: ' + host
            ) from exception

    def get_host(self) -> str:
        """
        Return server.
        """
        return self._host

    def send(self, text: str) -> None:
        """
        Send E-mail to server.

        text = E-mail header and body
        """
        sender = ''
        addresses = []
        for line in text.splitlines():
            if not line:
                break
            keyword = line.split(': ', 1)[0].lower()
            if keyword == 'from':
                sender = line.split(': ', 1)[1].strip()
            elif keyword in ('to', 'cc', 'bcc'):
                for address in line.split(': ', 1)[1].split(','):
                    addresses.append(address.strip())

        try:
            self._smtp.sendmail(sender, addresses, text)
        except Exception as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot send to STMP server: ' + self._host
            ) from exception


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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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

    def _create(self, options: Options) -> List[str]:
        subject = input("Subject: ")
        addresses = self._mail_alias(options.get_addresses())
        email = [
            'Subject: ' + subject,
            'To: ' + ', '.join(addresses),
            'From: ' + options.get_my_address(),
            'Reply-to: ' + options.get_my_address(),
            'X-Mailer: Qwikmail v' + options.get_release(),
            ''
        ]
        return email

    def _edit(self, options: Options) -> List[str]:
        try:
            with open(options.get_tmpfile(), 'w', newline='\n') as ofile:
                for line in self._email:
                    print(line, file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' +
                options.get_tmpfile() + '" temporary file.'
            ) from exception

        subtask_mod.Task(options.get_editor().get_cmdline()).run()

        try:
            with open(options.get_tmpfile(), errors='replace') as ifile:
                email = []
                for line in ifile:
                    email.append(line.rstrip('\r\n'))
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' +
                options.get_tmpfile() + '" temporary file.'
            ) from exception
        return email

    def _header(self) -> None:
        for line in self._email:
            print(line)
            if not line:
                break

    def _mail_alias(self, addresses: List[str]) -> List[str]:
        if self._malias.is_found():
            task = subtask_mod.Batch(self._malias.get_cmdline() + addresses)
            task.run(mode='batch')
            addresses = task.get_output()
        return addresses

    @staticmethod
    def _send(options: Options) -> None:
        print("Sending E-mail...")
        lines = []
        with open(options.get_tmpfile(), errors='replace') as ifile:
            for line in ifile:
                lines.append(line.rstrip('\r\n'))
        Mailer('localhost').send('\n'.join(lines))

        try:
            os.remove(options.get_tmpfile())
        except OSError:
            pass

    def _update(self) -> None:
        isemail = re.compile('(To|Cc|Bcc): ', re.IGNORECASE)
        for i in range(len(self._email)):
            if not self._email[i]:
                return
            if isemail.match(self._email[i]):
                self._email[i] = self._email[i].split()[0] + ' ' + ', '.join(
                    self._mail_alias([isemail.sub('', self._email[i])]))

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._malias = command_mod.Command('malias', errors='ignore')
        self._email = self._create(options)
        while True:
            self._email = self._edit(options)
            self._update()
            self._header()
            answer = input("Do you want to send E-mail (y/n)? ")
            if answer.lower() == 'y':
                self._send(options)
                break
            answer = input("Do you want to delete E-mail (y/n)? ")
            if answer.lower() == 'y':
                break

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
