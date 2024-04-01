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

# Find repo directories with no tags:
find /var/lib/registry/docker/registry/v2/repositories \
    -empty -type d -name tags
"""

import argparse
import fnmatch
import json
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple

import requests  # type: ignore

from config_mod import Config

# Maximum number of repositories (bug in Registry v2 returns only 100)
# Effects Go array size and huge number can crash Registry
MAXREPO = "99999"

requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

SSL_VERIFY = False


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._config()
        self.parse(sys.argv)

    def get_remove_flag(self) -> bool:
        """
        Return remove flag.
        """
        return self._args.remove_flag

    def get_urls(self) -> List[str]:
        """
        Return URls.
        """
        return self._args.urls

    @staticmethod
    def _config() -> None:
        if 'REQUESTS_CA_BUNDLE' not in os.environ:
            for file in (
                # Debian/Ubuntu
                '/etc/ssl/certs/ca-certificates.crt',
                # RHEL/CentOS
                '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'
            ):
                if Path(file).is_file():
                    os.environ['REQUESTS_CA_BUNDLE'] = file
                    break

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="List images in Docker registry.",
        )

        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help="Remove images.",
        )
        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help=(
                'Registry URL (ie "localhost:5000", "localhost:5000/debian*").'
            ),
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class DockerRegistry:
    """
    Docker Registry v1 class
    """

    def __init__(self, server: str) -> None:
        self._server = server
        config = Config()
        self._user_agent = config.get('user_agent')
        self._config()

    def get_url(self) -> str:
        """
        Return url.
        """
        return self._url

    def get_repositories(self) -> List[str]:
        """
        Return list repositories.
        """
        return self._repositories

    def _get_url(self, url: str) -> requests.Response:
        return requests.get(
            url,
            headers={'User-Agent': self._user_agent},
            verify=SSL_VERIFY,
            timeout=10,
        )

    def _config(self) -> None:
        self._url = self._server + '/v1/search'
        try:
            response = self._get_url(self._url)
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
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

    def get_info(self, repository: str, tag_match: str) -> dict:
        """
        Return repository tags information.
        """
        url = f'{self._server}/v1/repositories/{repository}/tags'
        info: dict = {}

        try:
            response = self._get_url(url)
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
        if response.status_code != 200:
            if response.status_code == 404:
                return info
            raise SystemExit(
                f'Requests "{url}" response code: {response.status_code}',
            )
        digests = response.json()
        tags = [tag for tag in digests if fnmatch.fnmatch(tag, tag_match)]

        for tag in tags:
            info[tag]['digest'] = digests[tag]
            info[tag]['image_id'] = digests[tag]
            info[tag]['timestamp'] = '????-??-??T??:??:??'
            info[tag]['size'] = 0

        return info

    def _delete_url(self, url: str) -> None:
        try:
            response = requests.delete(
                url,
                headers={'User-Agent': self._user_agent},
                verify=SSL_VERIFY,
                timeout=10,
            )
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
        # v2 returns 202, shared tags can 404
        if response.status_code not in (200, 202, 404):
            raise SystemExit(
                f'Requests "{url}" response code: {response.status_code}',
            )

    def delete(
        self,
        server: str,
        repository: str,
        tag: str,
        _: str,
    ) -> None:
        """
        Delete image
        """
        url = f"{server}/v1/repositories/{repository}/tags/{tag}"
        self._delete_url(url)


class DockerRegistry2(DockerRegistry):
    """
    Docker Registry v2 class
    """

    def _get_url(self, url: str) -> requests.Response:
        return requests.get(url, headers={
            'User-Agent': self._user_agent,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
        }, verify=SSL_VERIFY, timeout=10)

    def _config(self) -> None:
        self._url = f'{self._server}/v2/_catalog?n={MAXREPO}'
        try:
            response = self._get_url(self._url)
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
        if response.status_code == 200:
            try:
                self._repositories = response.json()['repositories']
            except ValueError:
                self._repositories = None
        else:
            self._repositories = None

    def get_time(self, repository: str, tag: str) -> str:
        """
        Return image creation time stamp (uses v1Compatibility mode).
        """
        url = f'{self._server}/v2/{repository}/manifests/{tag}'
        response = requests.get(url, headers={
            'User-Agent': self._user_agent,
            'Accept': 'application/vnd.docker.distribution.manifest.v1+json',
        }, verify=SSL_VERIFY, timeout=10)

        try:
            last_layer = response.json()['history'][0]['v1Compatibility']
            timestamp = json.loads(last_layer)['created'].split('.', 1)[0]
        except IndexError:
            timestamp = '????-??-??T??:??:??'
        return timestamp

    def get_info(self, repository: str, tag_match: str) -> dict:
        """
        Return repository tags information.
        """
        url = f'{self._server}/v2/{repository}/tags/list'
        info: dict = {}

        try:
            response = self._get_url(url)
        except Exception as exception:
            raise SystemExit(str(exception)) from exception
        if response.status_code != 200:
            if response.status_code == 404:
                return info
            raise SystemExit(
                f'Requests "{url}" response code: {response.status_code}',
            )

        tags = response.json()['tags']
        if tags:
            for tag in [x for x in tags if fnmatch.fnmatch(x, tag_match)]:
                info[tag] = {}
                url = f'{self._server}/v2/{repository}/manifests/{tag}'
                try:
                    response = self._get_url(url)
                except Exception as exception:
                    raise SystemExit(str(exception)) from exception
                if response.status_code != 200:
                    raise SystemExit(
                        f'Requests "{url}" response code: '
                        f'{response.status_code}',
                    )
                data = response.json()
                info[tag]['digest'] = response.headers['docker-content-digest']
                info[tag]['image_id'] = data['config']['digest']
                info[tag]['timestamp'] = self.get_time(repository, tag)
                info[tag]['size'] = sum(x['size'] for x in data['layers'])

        return info

    def delete(
        self,
        server: str,
        repository: str,
        tag: str,
        digest: str,
    ) -> None:
        """
        Delete image by untagging blobs before untagging manifest
        """
        url = f'{server}/v2/{repository}/manifests/{digest}'
        self._delete_url(url)


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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _get_registry(server: str) -> DockerRegistry:
        for Registry in (DockerRegistry2, DockerRegistry):
            registry = Registry(server)
            if registry.get_repositories() is not None:
                return registry

        raise SystemExit(f"Cannot find Docker Registry: {server}")

    @staticmethod
    def _breakup_url(url: str) -> Tuple[str, str, str]:
        if '://' not in url:
            url = (
                f'http://{url}'
                if url.startswith('localhost')
                else f'https://{url}'
            )
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
    def _check(cls, url: str, remove: bool = False) -> None:
        server, repo_match, tag_match = cls._breakup_url(url)
        registry = cls._get_registry(server)
        prefix = server.rsplit('://', 1)[-1]

        for repository in sorted(registry.get_repositories()):
            if fnmatch.fnmatch(repository, repo_match):
                info = registry.get_info(repository, tag_match)
                for tag in sorted(info):
                    image_id = info[tag]['image_id'].split(':', 1)[-1][:12]
                    timestamp = info[tag]['timestamp']
                    size = info[tag]['size'] / 1048576
                    image = f'{prefix}/{repository}:{tag}'
                    if remove:
                        print(
                            f"{image_id}  "
                            f"{timestamp} "
                            f"{size:8.2f}  "
                            f"{image}  DELETE",
                        )
                        registry.delete(
                            server,
                            repository,
                            tag,
                            info[tag]['digest'],
                        )
                    else:
                        print(f"{image_id}  {timestamp} {size:8.2f}  {image}")

    @classmethod
    def run(cls) -> int:
        """
        Run check
        """
        options = Options()

        print("IMAGE ID      CREATED             ZSIZE/MB  REPOSITORY:TAG")
        for url in options.get_urls():
            cls._check(url)

        if options.get_remove_flag():
            if input("\nPlease confirm image removal mode (y/n)? ") == 'y':
                for url in options.get_urls():
                    cls._check(url, remove=True)
            else:
                print("Aborted!")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
