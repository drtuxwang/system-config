#!/usr/bin/env python3
"""
Current weather search (using accuweather)

London: http://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328
"""

import argparse
import os
import signal
import sys
import time

import requests

import config_mod

if sys.version_info < (3, 4) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.4, < 4.0).")

# pylint: disable = no-member
requests.packages.urllib3.disable_warnings()
# pylint: enable = no-member


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_quiet_flag(self):
        """
        Return quiet flag.
        """
        return self._args.quiet_flag

    def get_url(self):
        """
        Return url.
        """
        return self._args.url[0]

    @staticmethod
    def _config():
        if 'REQUESTS_CA_BUNDLE' not in os.environ:
            for file in (
                    # Debian/Ubuntu
                    '/etc/ssl/certs/ca-certificates.crt',
                    # RHEL/CentOS
                    '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'
            ):
                if os.path.isfile(file):
                    os.environ['REQUESTS_CA_BUNDLE'] = file
                    break

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Current weather search.')

        parser.add_argument(
            '-q',
            action='store_true',
            dest='quiet_flag',
            help='Disable error messages'
        )
        parser.add_argument(
            'url',
            nargs=1,
            help='Weather data URL.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    @staticmethod
    def _parse(text):
        data = text.split('>Current Weather<')[-1].split('<!--')[0]
        if '<span class="large-temp">' in data:
            temp = data.split(
                '<span class="large-temp">'
            )[1].split('<')[0].replace('&deg;', '°C')
            if '<span class="cond">' in data:
                condition = data.split('<span class="cond">')[1].split('<')[0]
                return '{0:s} ({1:s})'.format(temp, condition)
        return None

    @classmethod
    def _search(cls, options):
        user_agent = config_mod.Config().get('user_agent')

        for _ in range(10):
            try:
                response = requests.get(
                    options.get_url(),
                    headers={'User-Agent': user_agent}
                )
            except requests.RequestException:
                break
            else:
                if response.status_code == 200:
                    weather = cls._parse(response.text)
                    if weather:
                        return weather
            time.sleep(2)

        if options.get_quiet_flag():
            return ''
        return '???C (???)'

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()
        print(cls._search(options))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
