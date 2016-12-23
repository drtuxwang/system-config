#!/usr/bin/env python3
"""
List all images in Docker registry

http://localhost:5000/v1/search
http://localhost:5000/v1/repositories/<repository>/tags
http://localhost:5000/v2/_catalog
http://localhost:5000/v2/<repository>/tags/list
http://localhost:5000/v2/<repository>/manifests/<tag>

"""

import argparse
import glob
import json
import os
import signal
import sys

import requests

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

requests.packages.urllib3.disable_warnings()

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
)


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_server(self):
        """
        Return server address.
        """
        return self._args.server[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='List all images in Docker registry.')

        parser.add_argument(
            'server',
            nargs=1,
            help='Server address (ie "http://localhost:5000").'
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
    def _check_registry1(options, repositories):
        print('#{0:s}/v1/search'.format(options.get_server()))
        api = options.get_server() + '/v1/repositories/{0:s}/tags'
        prefix = options.get_server().split('://')[-1]

        for repository in sorted(repositories):
            try:
                response = requests.get(
                    api.format(repository),
                    headers={'User-Agent': USER_AGENT},
                    allow_redirects=True,
                    verify=True
                )
            except Exception as exception:
                raise SystemExit(str(exception))
            if response.status_code != 200:
                raise SystemExit(
                    'Requests "{0:s}" response code: {1:d}'.format(
                        api.format(repository),
                        response.status_code
                    )
                )
            tags = json.loads(response.text).keys()
            for tag in sorted(tags):
                print('{0:s}/{1:s}:{2:s}'.format(prefix, repository, tag))

    @staticmethod
    def _check_registry2(options, repositories):
        print('#{0:s}/v2/_catalog'.format(options.get_server()))
        api = options.get_server() + '/v2/{0:s}/tags/list'
        prefix = options.get_server().split('://')[-1]

        for repository in sorted(repositories):
            try:
                response = requests.get(
                    api.format(repository),
                    headers={'User-Agent': USER_AGENT},
                    allow_redirects=True,
                    verify=True
                )
            except Exception as exception:
                raise SystemExit(str(exception))
            if response.status_code != 200:
                raise SystemExit(
                    'Requests "{0:s}" response code: {1:d}'.format(
                        api.format(repository),
                        response.status_code
                    )
                )
            tags = json.loads(response.text)['tags']
            for tag in sorted(tags):
                print('{0:s}/{1:s}:{2:s}'.format(prefix, repository, tag))

    @classmethod
    def run(cls):
        """
        Run check
        """
        options = Options()

        try:
            response = requests.get(
                options.get_server() + '/v2/_catalog',
                headers={'User-Agent': USER_AGENT},
                allow_redirects=True,
                verify=True
            )
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code == 200:
            repositories = json.loads(response.text)['repositories']
            cls._check_registry2(options, repositories)
        else:
            try:
                response = requests.get(
                    options.get_server() + '/v1/search',
                    headers={'User-Agent': USER_AGENT},
                    allow_redirects=True,
                    verify=True
                )
            except Exception as exception:
                raise SystemExit(str(exception))
            if response.status_code == 200:
                results = json.loads(response.text)['results']
                repositories = [
                    result['name'].replace('library/', '')
                    for result in results
                ]
                cls._check_registry1(options, repositories)
            else:
                raise SystemExit(
                    'Cannot find Docker Registry:' + options.get_server())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
