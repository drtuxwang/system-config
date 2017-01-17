#!/usr/bin/env python3
"""
List images in Docker registry

curl http://localhost:5000/v1/search
curl http://localhost:5000/v1/repositories/<name>/tags
curl -X DELETE http://localhost:5000/v1/repositories/<name>/tags/<tag>

curl http://localhost:5000/v2/_catalog?n=9999
curl http://localhost:5000/v2/<name>/tags/list
curl -v -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
    http://localhost:5000/v2/<name>/manifests/<tag>
curl -X DELETE http://localhost:5000/v2/<name>/manifests/<digest>
registry garbage-collect --dry-run /etc/docker/registry/config.yml
registry garbage-collect /etc/docker/registry/config.yml  # Reqistry restart
"""

import argparse
import fnmatch
import glob
import os
import signal
import sys

import requests

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# Maximum number of Docker Registry v2 repositories
# Effects Go array size and huge number crashes Registry
MAXREPO = "9999"

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

    def get_remove_flag(self):
        """
        Return remove flag.
        """
        return self._args.remove_flag

    def get_urls(self):
        """
        Return URls.
        """
        return self._args.urls

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='List images in Docker registry.')

        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help='Remove images.'
        )
        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help=(
                'Registry URL (ie "http://localhost:5000", '
                '"http://localhost:5000/debian*").'
            )
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
                results = response.json()['results']
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
        Return dictionary of tags mapped to keys
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
        return response.json()

    @staticmethod
    def _delete_url(url):
        try:
            response = requests.delete(url, headers={'User-Agent': USER_AGENT})
        except Exception as exception:
            raise SystemExit(str(exception))
        # v2 returns 202, shared tags can 404
        if response.status_code not in (200, 202, 404):
            raise SystemExit('Requests "{0:s}" response code: {1:d}'.format(
                url,
                response.status_code
            ))

    @classmethod
    def delete(cls, server, repository, tag, digest):
        """
        Delete image
        """
        print('{0:s}  {1:s}/{2:s}:{3:s}  DELETE'.format(
            digest, server.split('://')[-1], repository, tag))
        url = '{0:s}/v1/repositories/{1:s}/tags/{2:s}'.format(
            server, repository, tag)
        cls._delete_url(url)


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
        self._url = self._server + '/v2/_catalog?n=' + MAXREPO
        try:
            response = self._get_url(self._url)
        except Exception as exception:
            raise SystemExit(str(exception))
        if response.status_code == 200:
            try:
                self._repositories = response.json()['repositories']
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
        tags = response.json()['tags']
        if tags:
            for tag in tags:
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

    @classmethod
    def delete(cls, server, repository, tag, digest):
        """
        Delete image
        """
        print('{0:s}  {1:s}/{2:s}:{3:s}  DELETE'.format(
            digest, server.split('://')[-1], repository, tag))
        url = '{0:s}/v2/{1:s}/manifests/{2:s}'.format(
            server, repository, digest)
        cls._delete_url(url)


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
        if registry2.get_repositories() is not None:
            return registry2
        registry = DockerRegistry(server)
        if registry.get_repositories() is not None:
            return registry
        raise SystemExit('Cannot find Docker Registry: ' + server)

    @staticmethod
    def _breakup_url(url):
        if '://' not in url:
            url = 'http://' + url
        columns = url.split('/')
        server = '/'.join(columns[:3])
        repo_match = '/'.join(columns[3:])

        if repo_match:
            if ':' in repo_match:
                repo_match, tag_match = repo_match.split(':', 1)
            else:
                tag_match = '*'
        else:
            repo_match = '*'
            tag_match = '*'

        return (server, repo_match, tag_match)

    @classmethod
    def run(cls):
        """
        Run check
        """
        options = Options()
        remove = options.get_remove_flag()
        if remove:
            if input('\nPlease confirm image removal mode (y/n)? ') != 'y':
                raise SystemExit('Aborted!')

        for url in options.get_urls():
            server, repo_match, tag_match = cls._breakup_url(url)
            registry = cls._get_registry(server)
            prefix = server.split('://')[-1]

            for repository in sorted(registry.get_repositories()):
                if fnmatch.fnmatch(repository, repo_match):
                    digests = registry.get_tags(repository)
                    for tag in sorted(digests.keys()):
                        if fnmatch.fnmatch(tag, tag_match):
                            if remove:
                                registry.delete(
                                    server, repository, tag, digests[tag])
                            else:
                                print('{0:s}  {1:s}/{2:s}:{3:s}'.format(
                                    digests[tag], prefix, repository, tag))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
