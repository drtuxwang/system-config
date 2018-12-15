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

import dropbox

import logging_mod

if sys.version_info < (3, 4) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.4, < 4.0).")

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable=invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_command(self):
        """
        Return command.
        """
        return self._args.command[0]

    def get_urls(self):
        """
        Return URLs.
        """
        return self._args.urls

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='File sharing utility (currently dropbox only)'
        )

        parser.add_argument(
            'command',
            nargs=1,
            metavar='command',
            help='get|put.'
        )

        parser.add_argument(
            'urls',
            nargs='+',
            metavar='URL',
            help='URL (dropbox://file).'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
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

    def __init__(self):
        key = self._get_key()
        if key:
            self._client = self._connect(key)
        else:
            self._client = None

    @staticmethod
    def _get_key():
        file = os.environ.get('DROPBOX_KEY_FILE')
        if file:
            try:
                with open(file, errors='replace') as ifile:
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
    def _connect(key):
        client = dropbox.Dropbox(key)
        logger.info("Connecting to Dropbox server.")
        try:
            account = client.users_get_current_account()
        except (
                dropbox.exceptions.AuthError,
                dropbox.exceptions.BadInputError,
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

    def get(self, url):
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
            logger.error('Unable to download "dropbox:%s".', path)
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

    def put(self, url):
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
        except dropbox.exceptions.ApiError:
            logger.error('Unable to upload "dropbox:%s".', path)
            return False

        logger.info('Uploaded %d bytes.', len(data))
        return True


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
    def _get(urls):
        clients = {}
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
    def _put(urls):
        clients = {}
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

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        command = options.get_command()
        if command == 'get':
            errors = cls._get(options.get_urls())
        elif command == 'put':
            errors = cls._put(options.get_urls())
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
