#!/usr/bin/env python3
"""
List images in Docker registry

curl http://localhost:5000/v1/_ping
curl http://localhost:5000/v1/search
curl http://localhost:5000/v1/repositories/<repository>/tags
curl -X DELETE http://localhost:5000/v1/repositories/<repository>/tags/<tag>

curl http://localhost:5000/v2/
curl http://localhost:5000/v2/_catalog?n=9999
curl http://localhost:5000/v2/<repository>/tags/list
curl -v -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
    http://localhost:5000/v2/<repository>/manifests/<tag>
curl -X DELETE -I http://localhost:5500/v2/<repository>/blobs/<digest>
curl -X DELETE -I http://localhost:5000/v2/<repository>/manifests/<digest>
curl -X DELETE -I http://localhost:5000/v2/<repository>/blobmanifests/<digest>
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

import config_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

# Maximum number of repositories (bug in Registry v2 returns only 100)
# Effects Go array size and huge number can crash Registry
MAXREPO = "9999"

requests.packages.urllib3.disable_warnings()


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
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
                'Registry URL (ie "localhost:5000", "localhost:5000/debian*").'
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
        config = config_mod.Config()
        self._user_agent = config.get('user_agent')
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

    def _get_url(self, url):
        return requests.get(url, headers={'User-Agent': self._user_agent})

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

    def get_digests(self, repository):
        """
        Return digests dictionary for tags.
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
        digests = response.json()
        for tag in digests:
            digests[tag] = digests[tag]
        return digests

    def _delete_url(self, url):
        try:
            response = requests.delete(
                url,
                headers={'User-Agent': self._user_agent}
            )
        except Exception as exception:
            raise SystemExit(str(exception))
        # v2 returns 202, shared tags can 404
        if response.status_code not in (200, 202, 404):
            raise SystemExit('Requests "{0:s}" response code: {1:d}'.format(
                url,
                response.status_code
            ))

    def delete(self, server, repository, tag, digest):
        """
        Delete image
        """
        print("{0:s}  {1:s}/{2:s}:{3:s}  DELETE".format(
            digest, server.split('://')[-1], repository, tag))
        url = "{0:s}/v1/repositories/{1:s}/tags/{2:s}".format(
            server, repository, tag)
        self._delete_url(url)


class DockerRegistry2(DockerRegistry):
    """
    Docker Registry v2 class
    """

    def _get_url(self, url):
        return requests.get(url, headers={
            'User-Agent': self._user_agent,
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

    def get_digests(self, repository):
        """
        Return digests dictionary for tags.
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

    def delete(self, server, repository, tag, digest):
        """
        Delete image by untagging blobs before untagging manifest
        """
        print("{0:s}  {1:s}/{2:s}:{3:s}  DELETE".format(
            digest, server.split('://')[-1], repository, tag))
        url = '{0:s}/v2/{1:s}/manifests/{2:s}'.format(
            server, repository, digest)
        self._delete_url(url)


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
    def _get_registry(server, url):
        registry2 = DockerRegistry2(server)
        if registry2.get_repositories() is not None:
            print("\nDocker Registry API v2:", url.split('://')[-1])
            return registry2
        registry = DockerRegistry(server)
        if registry.get_repositories() is not None:
            print("\nDocker Registry API v1:", url.split('://')[-1])
            return registry
        raise SystemExit("Cannot find Docker Registry: " + server)

    @staticmethod
    def _breakup_url(url):
        if '://' not in url:
            if url.startswith('localhost'):
                url = 'http://' + url
            else:
                url = 'https://' + url
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

        return server, repo_match, tag_match

    @classmethod
    def _check(cls, url, remove=False):
        server, repo_match, tag_match = cls._breakup_url(url)
        registry = cls._get_registry(server, url)
        prefix = server.split('://')[-1]

        for repository in sorted(registry.get_repositories()):
            if fnmatch.fnmatch(repository, repo_match):
                digests = registry.get_digests(repository)
                for tag in sorted(digests):
                    if fnmatch.fnmatch(tag, tag_match):
                        if remove:
                            registry.delete(
                                server, repository, tag, digests[tag])
                        else:
                            print("{0:s}  {1:s}/{2:s}:{3:s}".format(
                                digests[tag], prefix, repository, tag))

    @classmethod
    def run(cls):
        """
        Run check
        """
        options = Options()
        for url in options.get_urls():
            cls._check(url)

        if options.get_remove_flag():
            if input("\nPlease confirm image removal mode (y/n)? ") == 'y':
                for url in options.get_urls():
                    cls._check(url, remove=True)
            else:
                print("Aborted!")


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
