#!/usr/bin/env python3
"""
Automatic connection to FTP server anonymously.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._ftp = syslib.Command('ftp')
        self._ftp.set_args(['-i', self._args.host[0]])

        self._netrc(self._args.host[0])

    def get_ftp(self):
        """
        Return ftp Command class object.
        """
        return self._ftp

    def _netrc(self, host):
        if 'HOME' in os.environ:
            netrc = os.path.join(os.environ['HOME'], '.netrc')
            umask = os.umask(int('077', 8))
            try:
                with open(netrc, 'w', newline='\n') as ofile:
                    print('machine', host,
                          'login anonymous password someone@somehost.somecompany.com', file=ofile)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + netrc +
                                 '" configuration file.')
            os.umask(umask)

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Automatic connection to FTP server anonymously.')

        parser.add_argument('host', nargs=1, help='Ftp host.')

        self._args = parser.parse_args(args)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        if os.name == 'nt':
            self._windows_argv()
        self._signals()
        try:
            options = Options(sys.argv)
            options.get_ftp().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
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
