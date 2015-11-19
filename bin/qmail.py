#!/usr/bin/env python3
"""
Quick commandline E-mailer.
"""

import argparse
import glob
import os
import re
import signal
import sys
import time

import syslib

RELEASE = '2.5.4'

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])

        os.umask(int('077', 8))

        self._sendmail = syslib.Command('sendmail', flags=['-t'], pathextra=['/usr/lib'])
        self._editor = syslib.Command('hedit', check=False)
        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        self._tmpfile = os.sep + os.path.join('tmp', 'qmail-' + syslib.info.getUsername() +
                                                     '.' + str(os.getpid()))
        if not self._editor.isFound():
            self._editor = syslib.Command('vi',)
        self._editor.setArgs([self._tmpfile])
        self._myAddress = self._address()

    def getAddresses(self):
        """
        Return my addresses.
        """
        return self._args.addresses

    def getEditor(self):
        """
        Return editor Command class object.
        """
        return self._editor

    def getMyAddress(self):
        """
        Return my address.
        """
        return self._myAddress

    def getRelease(self):
        """
        Return release version.
        """
        return self._release

    def getSendmail(self):
        """
        Return sendmail Command class object.
        """
        return self._sendmail

    def getTmpfile(self):
        """
        Return tmpfile.
        """
        return self._tmpfile

    def _address(self):
        file = os.path.join(os.environ['HOME'], '.address')
        if os.path.isfile(file):
            try:
                with open(file, errors='replace') as ifile:
                    myAddress = ifile.readline().strip()
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" configuration file.')
        else:
            myAddress = syslib.info.getUsername()
            try:
                with open(file, 'w', newline='\n') as ofile:
                    print(myAddress.encode(), file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" configuration file.')
        return myAddress

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Qwikmail v' + self._release + ', Quick commandline E-mailer.')

        parser.add_argument('addresses', nargs='+', metavar='address', help='E-mail addresses.')

        self._args = parser.parse_args(args)


class Mailer:

    def __init__(self, options):
        self._malias = syslib.Command('malias', check=False)
        self._create(options)
        while True:
            self._edit(options)
            self._update()
            self._header()
            answer = input('Do you want to send E-mail (y/n)? ')
            if answer.lower() == 'y':
                self._send(options)
                break
            else:
                answer = input('Do you want to delete E-mail (y/n)? ')
                if answer.lower() == 'y':
                    break

    def _create(self, options):
        subject = input('Subject: ')
        addresses = self._mailAlias(options.getAddresses())
        self._email = ['Subject: ' + subject, 'To: ' + ', '.join(addresses),
                       'From: ' + options.getMyAddress(), 'Reply-to: ' + options.getMyAddress(),
                       'X-Mailer: Qwikmail v' + options.getRelease(), '']

    def _edit(self, options):
        try:
            with open(options.getTmpfile(), 'w', newline='\n') as ofile:
                for line in self._email:
                    print(line, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' +
                             options.getTmpfile() + '" temporary file.')
        options.getEditor().run()
        try:
            with open(options.getTmpfile(), errors='replace') as ifile:
                self._email = []
                for line in ifile:
                    self._email.append(line.rstrip('\r\n'))
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' +
                             options.getTmpfile() + '" temporary file.')

    def _header(self):
        for line in self._email:
            print(line)
            if not line:
                break

    def _mailAlias(self, addresses):
        if self._malias.isFound():
            self._malias.setArgs(addresses)
            self._malias.run(mode='batch')
            addresses = self._malias.getOutput()
        return addresses

    def _send(self, options):
        print('Sending E-mail...')
        sendmail = options.getSendmail()
        sendmail.run(mode='batch', stdin=self._email)
        if not sendmail.hasOutput():
            try:
                os.remove(options.getTmpfile())
            except OSError:
                pass
        for line in sendmail.getOutput() + sendmail.getError():
            print(line)
        if sendmail.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(sendmail.getExitcode()) +
                             ' received from "' + sendmail.getFile() + '".')

    def _update(self):
        isemail = re.compile('(To|Cc|Bcc): ', re.IGNORECASE)
        for i in range(len(self._email)):
            if not self._email[i]:
                return
            elif isemail.match(self._email[i]):
                self._email[i] = (self._email[i].split()[0] + ' ' +
                                  ', '.join(self._mailAlias([isemail.sub('', self._email[i])])))


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Mailer(options)
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
