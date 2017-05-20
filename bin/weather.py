#!/usr/bin/env python3
"""
Current weather search (using accuweahther)

London: http://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328
"""

import argparse
import os
import signal
import sys

import requests

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

requests.packages.urllib3.disable_warnings()


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_url(self):
        """
        Return url.
        """
        return self._args.url

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

    @staticmethod
    def _search(url):
        user_agent = (
            'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) '
            'Gecko/20100101 Firefox/45.0'
        )

        try:
            response = requests.get(url, headers={'User-Agent': user_agent})
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code != 200:
            raise SystemExit(
                'Requests response code: ' + str(response.status_code))

        data = response.text.split('>Current Weather<')[-1].split('<!--')[0]
        if '<span class="large-temp">' in data:
            temp = data.split('<span class="large-temp">')[1].split('<')[0]
            if '<span class="cond">' in data:
                condition = data.split('<span class="cond">')[1].split('<')[0]
                print('{0:s} ({1:s})'.format(
                    temp.replace('&deg;', 'C'),
                    condition
                ))
                return
        print('???C (???)')

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()
        cls._search(" ".join(options.get_url()))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()