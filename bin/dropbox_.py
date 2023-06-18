#!/usr/bin/env python3
"""
Dropbox file sharing client
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List

# pylint: disable=import-error
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

    def get_action(self) -> str:
        """
        Return action.
        """
        return self._args.action[0]

    def get_files(self) -> List[str]:
        """
        Return files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Dropbox file sharing client.",
        )

        parser.add_argument(
            'action',
            nargs=1,
            metavar='action',
            help="ls|get|put|rm.",
        )

        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="file upload/download/delete.",
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
                with Path(file).open(errors='replace') as ifile:
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
    def _connect(key: str) -> dropbox.dropbox_client.Dropbox:
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

    def list(self, files: List[str]) -> int:
        """
        List Dropbox path.
        """
        if self._client is None:
            logger.warning('No dropbox connection"')
            return max(1, len(files))

        errors = 0
        for file in files if files else ['']:
            logger.info('Listing "dropbox://%s".', file)
            try:
                entries = self._client.files_list_folder(
                    file,
                    recursive=True,
                ).entries
                for entry in sorted(entries, key=lambda s: s.name):
                    print(
                        f"{entry.size:10d} "
                        f"[{entry.client_modified}] "
                        f"{entry.name}",
                    )
            except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
                logger.error('Unable to list "dropbox://%s".', file)
                errors += 1
            except stone.backends.python_rsrc.stone_validators.ValidationError:
                logger.info('Found 0 files.')
            else:
                logger.info('Found %d files.', len(entries))

        return errors

    def download(self, files: List[str]) -> int:
        """
        Download Dropbox path to file.
        """
        if self._client is None:
            logger.warning('No dropbox connection"')
            return len(files)

        errors = 0
        for file in files:
            name = Path(file).name
            logger.info('Downloading "dropbox://%s" to "%s".', file, name)
            try:
                metadata, response = self._client.files_download(f'/{file}')
                with Path(name).open('wb') as ofile:
                    ofile.write(response.content)
                file_time = time.mktime(metadata.server_modified.timetuple())
                os.utime(name, (file_time, file_time))
                logger.info('Downloaded %d bytes.', len(response.content))
            except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
                logger.error('Unable to download "dropbox://%s".', file)
                errors += 1
            except OSError:
                logger.error('Cannot write "%s" file.', name)
                errors += 1

        return errors

    def upload(self, files: List[str]) -> int:
        """
        Upload file to Dropbox path.
        """
        if self._client is None:
            logger.warning('No dropbox connection"')
            return len(files)

        errors = 0
        for file in files:
            name = Path(file).name
            logger.info('Uploading "%s" to "dropbox://%s".', name, file)
            try:
                with Path(name).open('rb') as ifile:
                    data = ifile.read()
                self._client.files_upload(
                    data,
                    f'/{file}',
                    mode=dropbox.files.WriteMode('overwrite'),
                )
            except OSError:
                logger.error('Cannot read "%s" file.', name)
                errors += 1
            except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
                logger.error('Unable to upload "dropbox://%s".', file)
                errors += 1
            logger.info('Uploaded %d bytes.', len(data))

        return errors

    def remove(self, files: List[str]) -> int:
        """
        Remove Dropbox path.
        """
        if self._client is None:
            logger.warning('No dropbox connection"')
            return len(files)

        errors = 0
        for file in files:
            logger.info('Removing "dropbox://%s".', file)
            try:
                if file == '/':
                    logger.error('Unsafe to remove all files "%s".', file)
                    errors += 1
                else:
                    entry = self._client.files_delete(f'/{file}')
                    print(
                        f"{entry.size:10d} "
                        f"[{entry.client_modified}] "
                        f"{entry.name}  # Removed",
                    )
            except (dropbox.exceptions.ApiError, dropbox.exceptions.HttpError):
                logger.error('Unable to remove "dropbox://%s".', file)
                errors += 1

        return errors


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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        action = options.get_action()
        files = options.get_files()

        client = DropboxClient()
        if action == 'ls':
            errors = client.list(files)
        elif action == 'get':
            errors = client.download(files)
        elif action == 'put':
            errors = client.upload(files)
        elif action == 'rm':
            errors = client.remove(files)
        else:
            logger.error("Invalid action: %s", action)
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
