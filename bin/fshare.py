#!/usr/bin/env python3
"""
File sharing utility (currently dropbox only)
"""

import argparse
import logging
import os
import signal
import sys
import time
from typing import List, Optional

import dropbox  # type: ignore
import requests  # type: ignore
import stone.backends.python_rsrc.stone_validators  # type: ignore

import logging_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_command(self) -> str:
        """
        Return command.
        """
        return self._args.command[0]

    def get_urls(self) -> List[str]:
        """
        Return URLs.
        """
        return self._args.urls

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="File sharing utility (currently dropbox only)",
        )

        parser.add_argument(
            'command',
            nargs=1,
            metavar='command',
            help="get|put.",
        )

        parser.add_argument(
            'urls',
            nargs='+',
            metavar='URL',
            help="URL (dropbox://file).",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class DropboxClient:
    """
    Dropbox file transfer class

    https://www.dropbox.com/developers/apps/create
      Create App & Generated access token
    """

    def __init__(self) -> None:
        key = self._get_key()
        if key:
            self._client = self._connect(key)
        else:
            self._client = None

    @staticmethod
    def _get_key() -> str:
        file = os.environ.get('DROPBOX_KEY_FILE')
        if file:
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    return ifile.readline().strip()
            except OSError:
                logger.error('Cannot read "%s" file.', file)
            else:
                logger.info("DROPBOX_KEY_FILE=%s", file)
        else:
            logger.error(
                "DROPBOX_KEY_FILE not set to key file location."
            )
        return None

    @staticmethod
    def _connect(key: str) -> Optional[dropbox.dropbox_client.Dropbox]:
        client = dropbox.Dropbox(key)
        logger.info("Connecting to Dropbox server.")
        try:
            account = client.users_get_current_account()
        except (
                dropbox.exceptions.AuthError,
                dropbox.exceptions.BadInputError,
                requests.exceptions.ConnectionError,
        ):
            logger.error("Unable to connect and login to Dropbox server.")
        else:
            logger.info(
                "Connected to account: %s %s (%s)",
                account.name.given_name,
                account.name.surname,
                account.account_id
            )
            return client
        return None

    def list(self, url: str) -> bool:
        """
        List Dropbox path.
        """
        if self._client is None:
            logger.warning("No dropbox connection: %s", url)
            return False

        path = url.split('dropbox://', 1)[1]
        logger.info('Listing "%s".', url)

        try:
            entries = self._client.files_list_folder(
                path,
                recursive=True,
            ).entries
            for entry in sorted(entries, key=lambda s: s.name):
                print(
                    f"{entry.size:10d} "
                    f"[{entry.client_modified}] "
                    f"{entry.name}",
                )
        except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
            logger.error('Unable to list "%s".', url)
            return False
        except stone.backends.python_rsrc.stone_validators.ValidationError:
            logger.info('Found 0 files.')
        else:
            logger.info('Found %d files.', len(entries))
        return True

    def get(self, url: str) -> bool:
        """
        Download Dropbox path to file.
        """
        if self._client is None:
            logger.warning("No dropbox connection: %s", url)
            return False

        path = url.split('dropbox:/', 1)[1]
        file = os.path.basename(url)
        logger.info('Downloading "%s" to "%s".', url, file)

        try:
            metadata, response = self._client.files_download(path)
        except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
            logger.error('Unable to download "%s".', url)
            return False

        try:
            with open(file, 'wb') as ofile:
                ofile.write(response.content)
        except OSError:
            logger.error('Cannot write "%s" file.', file)
            return False
        file_time = time.mktime(metadata.server_modified.timetuple())
        os.utime(file, (file_time, file_time))

        logger.info('Downloaded %d bytes.', len(response.content))
        return True

    def put(self, url: str) -> bool:
        """
        Upload file to Dropbox path.
        """
        if self._client is None:
            logger.warning("No dropbox connection: %s", url)
            return False

        path = url.split('dropbox:/', 1)[1]
        file = os.path.basename(url)
        logger.info('Uploading "%s" to "%s".', file, url)

        try:
            with open(file, 'rb') as ifile:
                data = ifile.read()
        except OSError:
            logger.error('Cannot read "%s" file.', file)
            return False

        try:
            self._client.files_upload(
                data,
                path,
                mode=dropbox.files.WriteMode('overwrite')
            )
        except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
            logger.error('Unable to upload "%s".', url)
            return False

        logger.info('Uploaded %d bytes.', len(data))
        return True

    def remove(self, url: str) -> bool:
        """
        Remove Dropbox path.
        """
        if self._client is None:
            logger.warning("No dropbox connection: %s", url)
            return False

        path = url.split('dropbox:/', 1)[1]
        logger.info('Removing "%s".', url)

        if path == '/':
            logger.error('Unsafe to remove all files "%s".', url)
            return False

        try:
            entry = self._client.files_delete(path)
        except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
            logger.error('Unable to remove "%s".', url)
            return False

        print(
            f"{entry.size:10d} "
            f"[{entry.client_modified}] "
            f"{entry.name}  # Removed",
        )

        return True


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

    @staticmethod
    def _list(urls: List[str]) -> int:
        clients: dict = {}
        errors = 0

        for url in urls:
            if url.startswith('dropbox://'):
                if not clients.get('dropbox'):
                    clients['dropbox'] = DropboxClient()
                if not clients['dropbox'].list(url):
                    errors += 1
            else:
                logger.error("Unsupported URL: %s", url)
                errors += 1
        return errors

    @staticmethod
    def _get(urls: List[str]) -> int:
        clients: dict = {}
        errors = 0

        for url in urls:
            if url.startswith('dropbox://'):
                if not clients.get('dropbox'):
                    clients['dropbox'] = DropboxClient()
                if not clients['dropbox'].get(url):
                    errors += 1
            else:
                logger.error("Unsupported URL: %s", url)
                errors += 1
        return errors

    @staticmethod
    def _put(urls: List[str]) -> int:
        clients: dict = {}
        errors = 0

        for url in urls:
            if url.startswith('dropbox://'):
                if not clients.get('dropbox'):
                    clients['dropbox'] = DropboxClient()
                if not clients['dropbox'].put(url):
                    errors += 1
            else:
                logger.error("Unsupported URL: %s", url)
                errors += 1
        return errors

    @staticmethod
    def _remove(urls: List[str]) -> int:
        clients: dict = {}
        errors = 0

        for url in urls:
            if url.startswith('dropbox://'):
                if not clients.get('dropbox'):
                    clients['dropbox'] = DropboxClient()
                if not clients['dropbox'].remove(url):
                    errors += 1
            else:
                logger.error("Unsupported URL: %s", url)
                errors += 1
        return errors

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        command = options.get_command()
        if command == 'ls':
            errors = cls._list(options.get_urls())
        elif command == 'get':
            errors = cls._get(options.get_urls())
        elif command == 'put':
            errors = cls._put(options.get_urls())
        elif command == 'rm':
            errors = cls._remove(options.get_urls())
        else:
            logger.error("Invalid command: %s", command)
            return 1

        if errors:
            logger.error("Total errors: %d", errors)
            return 1
        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
