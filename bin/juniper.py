#!/usr/bin/env python3
"""
Connect to Juniper Network Connect VPN.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        if self._args.guiFlag:
            xterm = syslib.Command('xterm')
            xterm.set_flags([
                '-fn', '-misc-fixed-bold-r-normal--18-*-iso8859-1', '-fg', '#000000',
                '-bg', '#ffffdd', '-cr', '#ff0000', '-geometry', '19x3', '-ut', '+sb', '-e'])
            xterm.set_args(args[:1] + self._args.site)
            xterm.run(mode='daemon')
            raise SystemExit(0)

        site = self._args.site[0]
        if site.count('@') not in (0, 1) or site.count('/') != 1:
            raise SystemExit(sys.argv[0] + ': Invalid Juniper site "' + site + '" format.')

        if '@' not in site:
            self._username = ''
        else:
            self._username = site.split('@')[0]
        self._server = site.split('@')[-1].split('/')[0]
        self._domain = site.split('/')[-1]

        self._vpn(args)

    def get_certificate(self):
        """
        Return certificate location.
        """
        return self._certificate

    def get_ncsvc(self):
        """
        Return ncsvc Command class object.
        """
        return self._ncsvc

    def _config(self):
        configdir = '/root/.juniper_networks'
        if not os.path.isdir(configdir):
            try:
                os.makedirs(configdir)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + configdir + '" directory.')
        self._certificate = os.path.join(configdir, self._server + '.ssl')

    def _openssl(self):
        os.umask(int('077', 8))
        self._config()
        print('Creating "' + self._certificate + '" certificate...')
        openssl = syslib.Command('openssl')
        openssl.set_args(['s_client', '-connect', self._server + ':443'])
        openssl.run(mode='batch')
        if openssl.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(openssl.get_exitcode()) +
                             ' received from "' + openssl.get_file() + '".')
        certificate = openssl.get_output()
        openssl.set_args(['verify'])
        openssl.run(mode='batch', stdin=certificate)
        openssl.set_args(['x509', '-outform', 'der', '-out', self._certificate])
        openssl.run(stdin=certificate)
        if openssl.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(openssl.get_exitcode()) +
                             ' received from "' + openssl.get_file() + '".')

    def _vpn(self, args):
        self._ncsvc = syslib.Command('ncsvc', check=False)
        if not self._ncsvc.is_found():
            juniper = syslib.Command('juniper', check=False)
            if juniper.is_found():
                juniper.set_args(args[1:])
                juniper.run(mode='exec')
            self._ncsvc = syslib.Command('ncsvc')
        if syslib.info.get_username() != 'root':
            sudo = syslib.Command('sudo', args=['python3'] + args)
            sudo.run(mode='exec')
        self._openssl()
        self._ncsvc.set_args(['-v'])
        self._ncsvc.run()
        if not self._username:
            self._username = input('Username: ').strip()
        self._ncsvc.set_args(['-u', self._username, '-h', self._server, '-r', self._domain,
                              '-f', self._certificate, '-L', '1'])
        if os.path.isfile('/etc/jnpr-nc-resolv.conf'):
            try:
                os.rename('/etc/jnpr-nc-resolv.conf', '/etc/resolv.conf')
            except OSError:
                pass

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Connect to Juniper Network Connect VPN.')

        parser.add_argument('-g', dest='guiFlag', action='store_true', help='Start GUI.')

        parser.add_argument('site', nargs=1, metavar='[user@]site/domain', help='Juniper server.')

        self._args = parser.parse_args(args)


class NetworkConnect(object):
    """
    Network connect class
    """

    def __init__(self, options):
        self._signal_trap()
        options.get_ncsvc().run()
        time.sleep(4)

    def _signal_trap(self):
        signal.signal(signal.SIGINT, self._xterm_network_connect)
        signal.signal(signal.SIGTERM, self._xterm_network_connect)

    def _xterm_network_connect(self, signal, frame):
        print('\nTerminating...')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            NetworkConnect(options)
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
