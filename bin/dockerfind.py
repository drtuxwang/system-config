#!/usr/bin/env python3
"""
List images in Docker registry

curl http://localhost:5000/v1/search
curl http://localhost:5000/v1/repositories/<name>/tags

curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/<name>/tags/list
curl -v -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
    http://localhost:5000/v2/<name>/manifests/<tag>
curl -X DELETE http://localhost:5000/v2/<name>/manifests/<digest>
registry garbage-collect --dry-run /etc/docker/registry/config.yml
registry garbage-collect /etc/docker/registry/config.yml  # Reqistry restart
"""

import argparse
import glob
import json
import os
import re
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

    def get_pattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='List images in Docker registry.')

        parser.add_argument(
            'server',
            nargs=1,
            help='Server address (ie "http://localhost:5000").'
        )
        parser.add_argument(
            'pattern',
            nargs='?',
            default='.*',
            help='Regular expression.'
        )

        self._args = parser.parse_args(args)

        if '://' not in self._args.server[0]:
            self._args.server[0] = 'http://' + self._args.server[0]

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if '://' not in self._args.server[0]:
            raise SystemExit(sys.argv[0] + ': Expected "://" missing in URL')


class DockerRegistry(object):
    """
    Docker Registry v1 class
    """

    def __init__(self, server):
        self._server = server
        self._config()

    def get_url(self):
        """
        Return url.
        """
        return self._url

    def get_repositories(self):
        """
        Return list repositories.
        """
        return self._repositories

    @staticmethod
    def _get_url(url):
        return requests.get(url, headers={'User-Agent': USER_AGENT})

    def _config(self):
        self._url = self._server + '/v1/search'
        try:
            response = self._get_url(self._url)
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code == 200:
            try:
                results = json.loads(response.text)['results']
            except ValueError:
                self._repositories = None
            else:
                self._repositories = [
                    result['name'].replace('library/', '')
                    for result in results
                ]
        else:
            self._repositories = None

    def get_tags(self, repository):
        """
        Return dictionay of tags mapped to keys
        """
        url = self._server + '/v1/repositories/' + repository + '/tags'
        try:
            response = self._get_url(url)
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code != 200:
            if response.status_code == 404:
                return {}
            raise SystemExit('Requests "{0:s}" response code: {1:d}'.format(
                url,
                response.status_code
            ))
        return json.loads(response.text)


class DockerRegistry2(DockerRegistry):
    """
    Docker Registry v2 class
    """

    @staticmethod
    def _get_url(url):
        return requests.get(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
        })

    def _config(self):
        self._url = self._server + '/v2/_catalog'
        try:
            response = self._get_url(self._url)
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code == 200:
            try:
                self._repositories = json.loads(response.text)['repositories']
            except ValueError:
                self._repositories = None
        else:
            self._repositories = None

    def get_tags(self, repository):
        """
        Return tags.
        """
        url = self._server + '/v2/' + repository + '/tags/list'
        try:
            response = self._get_url(url)
        except Exception as exception:
            raise SystemExit(str(exception))
        digests = {}
        if response.status_code != 200:
            if response.status_code == 404:
                return digests
            raise SystemExit('Requests "{0:s}" response code: {1:d}'.format(
                url,
                response.status_code
            ))
        for tag in json.loads(response.text)['tags']:
            url = self._server + '/v2/' + repository + '/manifests/' + tag
            try:
                response = self._get_url(url)
            except Exception as exception:
                raise SystemExit(str(exception))
            if response.status_code != 200:
                raise SystemExit(
                    'Requests "{0:s}" response code: {1:d}'.format(
                        url, response.status_code))
            digests[tag] = response.headers['docker-content-digest']

        return digests


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
    def _get_registry(server):
        registry2 = DockerRegistry2(server)
        if registry2.get_repositories():
            return registry2
        registry = DockerRegistry(server)
        if registry.get_repositories():
            return registry
        raise SystemExit('Cannot find Docker Registry:' + server)

    @classmethod
    def run(cls):
        """
        Run check
        """
        options = Options()
        server = options.get_server()

        registry = cls._get_registry(server)
        prefix = server.split('://')[-1]
        ismatch = re.compile(options.get_pattern())
        for repository in sorted(registry.get_repositories()):
            if ismatch.search(repository):
                digests = registry.get_tags(repository)
                for tag in sorted(digests.keys()):
                    print('{0:s}  {1:s}/{2:s}:{3:s}'.format(
                        digests[tag], prefix, repository, tag))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
