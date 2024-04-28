#!/usr/bin/env python3
"""
Python file handling utility module

Copyright GPL v2: 2006-2024 By Dr Colin Kong
"""

import getpass
import re
import time
from pathlib import Path
from typing import Any, Union

RELEASE = '2.7.0'
VERSION = 20240421


class FileStat:
    """
    This class contains file status information.

    self._file = Filename
    self._stat = Dictionary of stats
    """

    def __init__(
        self,
        file: Any = None,
        size: int = None,
        follow_symlinks: bool = True,
    ) -> None:
        """
        file = filename
        size = Override file size (useful for zero sizing links)
        """
        self._file = str(file)
        self._stat: dict = {}
        if file:
            path = Path(file)
            try:
                if not follow_symlinks and path.is_symlink():
                    file_stat = path.lstat()
                else:
                    file_stat = path.stat()
                self._stat['device'] = file_stat.st_dev
                self._stat['inode'] = file_stat.st_ino
                self._stat['nlink'] = file_stat.st_nlink
                self._stat['mode'] = file_stat.st_mode
                self._stat['userid'] = file_stat.st_uid
                self._stat['groupid'] = file_stat.st_gid
                self._stat['size'] = file_stat.st_size
                self._stat['atime'] = file_stat.st_atime
                self._stat['mtime'] = file_stat.st_mtime
                self._stat['ctime'] = file_stat.st_ctime
            except (OSError, TypeError) as exception:
                if path.exists() and not path.is_symlink():
                    raise FileStatNotFoundError(
                        f"Cannot find status: {path}",
                    ) from exception
            else:
                if size is not None:
                    self._size = size

    def get_file(self) -> str:
        """
        Return filename
        """
        return self._file

    def get_mode(self) -> int:
        """
        Return inode protection mode
        """
        return self._stat.get('mode', 0)

    def get_inode_number(self) -> int:
        """
        Return inode number
        """
        return self._stat.get('inode', 0)

    def get_inode_device(self) -> int:
        """
        Return device inode resides on
        """
        return self._stat.get('device', 0)

    def get_number_links(self) -> int:
        """
        Return number of links to the inode
        """
        return self._stat.get('nlink', 0)

    def get_userid(self) -> int:
        """
        Return user ID of the file owner
        """
        return self._stat.get('userid', 0)

    def get_groupid(self) -> int:
        """
        Return group ID of the file owner
        """
        return self._stat.get('groupid', 0)

    def get_size(self) -> int:
        """
        Return size in bytes of a file
        """
        return self._stat.get('size', 0)

    def get_date_local(self) -> str:
        """
        Return date of last modification in ISO local date format
        (ie '2011-12-31')
        """
        return time.strftime('%Y-%m-%d', time.localtime(self.get_mtime()))

    def get_atime(self) -> float:
        """
        Return time of last access
        """
        return self._stat.get('atime', 0.)

    def get_atime_local(self) -> str:
        """
        Return time of last access in ISO8601 format
        (ie '2011-12-31T12:30:28.123+0100')
        """
        return time.strftime(
            f'%Y-%m-%dT%H:%M:%S.{f"{int(self.get_atime() % 1 * 1000):03d}"}%z',
            time.localtime(self.get_atime())
        )

    def get_mtime(self) -> float:
        """
        Return time of last access
        """
        return self._stat.get('mtime', 0.)

    def get_mtime_local(self) -> str:
        """
        Return time of last modification in ISO8601 format
        (ie '2011-12-31T12:30:28.123+0100')
        """
        return time.strftime(
            f'%Y-%m-%dT%H:%M:%S.{f"{int(self.get_mtime() % 1 * 1000):03d}"}%z',
            time.localtime(self.get_mtime())
        )

    def get_ctime(self) -> float:
        """
        Return time of last meta data change.
        """
        return self._stat.get('ctime', 0.)

    def get_ctime_local(self) -> str:
        """
        Return time of last meta data change in ISO8601 format
        (ie '2011-12-31T12:30:28.123+0100')
        """
        return time.strftime(
            f'%Y-%m-%dT%H:%M:%S.{f"{int(self.get_ctime() % 1 * 1000):03d}"}%z',
            time.localtime(self.get_ctime())
        )

    def get_time_local(self) -> str:
        """
        Return time of last modification in full ISO format (deprecated)
        (ie '2011-12-31-12:30:28')
        """
        return time.strftime(
            '%Y-%m-%d-%H:%M:%S',
            time.localtime(self.get_mtime())
        )

    def get_time_access(self) -> int:
        """
        Return time of last access in seconds (deprecated)
        """
        return int(self.get_atime())

    def get_time(self) -> int:
        """
        Return time of last modification in seconds (deprecated)
        """
        return int(self.get_mtime())

    def get_time_change(self) -> int:
        """
        Return time of last meta data change in seconds (deprecated)
        """
        return int(self.get_ctime())


class FileUtil:
    """
    This class contains file utilites.
    """

    @staticmethod
    def newest(files: list) -> str:
        """
        Return newest file or directory.

        files = List of files
        """
        path_new = None
        new_time = -1.
        paths = [Path(x) for x in files]
        for path in [x for x in paths if x.exists() and not x.is_symlink()]:
            file_time = path.stat().st_mtime
            if file_time > new_time:
                path_new = path
                new_time = file_time

        return str(path_new)

    @staticmethod
    def oldest(files: list) -> str:
        """
        Return oldest file or directory.

        files = List of files
        """
        path_new = None
        new_time = float('inf')
        paths = [Path(x) for x in files]
        for path in [x for x in paths if x.exists() and not x.is_symlink()]:
            file_time = path.stat().st_mtime
            if file_time < new_time:
                path_new = path
                new_time = file_time

        return str(path_new)

    @staticmethod
    def strings(file: str, pattern: str) -> str:
        """
        Return first match of pattern in binary file
        """
        is_match = re.compile(pattern)
        try:
            with Path(file).open('rb') as ifile:
                string = ''
                while True:
                    data = ifile.read(4096)
                    if not data:
                        break
                    for byte in data:
                        if 31 < byte < 127:
                            string += chr(byte)
                        else:
                            if len(string) >= 4:
                                if is_match.search(string):
                                    return string
                            string = ''
            if len(string) >= 4:
                if is_match.search(string):
                    return string
        except OSError:
            pass
        return ''

    @staticmethod
    def tmpdir(name: Union[str, Path] = None) -> str:
        """
        Return temporary directory with prefix and set permissions.
        """
        path = Path('/tmp', getpass.getuser())
        if name:
            path = Path(path, name)

        if not path.is_dir():
            try:
                path.mkdir(parents=True)
            except OSError as exception:
                raise FileTmpdirCreationError(
                    f'Cannot create directory: {path}',
                ) from exception

        try:
            path.chmod(0o700)
        except OSError as exception:
            raise FileTmpdirPermissionError(
                f'Permission error: {path}',
            ) from exception

        return str(path)


class FileError(Exception):
    """
    File module error class.
    """


class FileStatNotFoundError(FileError):
    """
    File stat not found error class.
    """


class FileTmpdirCreationError(FileError):
    """
    File tmpdir creation error class.
    """


class FileTmpdirPermissionError(FileError):
    """
    File tmpdir permission error class.
    """


if __name__ == '__main__':
    help(__name__)
