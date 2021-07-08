#!/usr/bin/env python3
"""
Google search.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import requests  # type: ignore

import config_mod

requests.packages.urllib3.disable_warnings()  # pylint: disable = no-member


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._config()
        self.parse(sys.argv)

    def get_keywords(self) -> List[str]:
        """
        Return list of keywords.
        """
        return self._args.keywords

    @staticmethod
    def _config() -> None:
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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description='Google search.')

        parser.add_argument(
            'keywords',
            nargs='+',
            metavar='keyword',
            help='Keyword to search.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    @staticmethod
    def _search(search_for: str) -> None:
        url = (
            'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&' +
            search_for
        )
        user_agent = config_mod.Config().get('user_agent')

        try:
            response = requests.get(
                url,
                params={'q': search_for},
                headers={'User-Agent': user_agent},
                allow_redirects=True,
                verify=True
            )
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
        if response.status_code != 200:
            raise SystemExit(
                'Requests response code: ' + str(response.status_code))

        print(response.url)
        for page in response.json()['responseData']['results']:
            print("    {0:s}".format(page['unescapedUrl']))
            print("        {0:s}".format(page['titleNoFormatting']))

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        cls._search(" ".join(options.get_keywords()))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
