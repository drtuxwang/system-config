#!/usr/bin/env python3
"""
Python file handling utility module

Copyright GPL v2: 2006-2022 By Dr Colin Kong
"""

import getpass
import os
import re
import time
from typing import List

RELEASE = '2.5.2'
VERSION = 20220402


class FileStat:
    """
    This class contains file status information.

    self._file = Filename
    self._stat = Dictionary of stats
    """

    def __init__(
        self,
        file: str = '',
        size: int = None,
        follow_symlinks: bool = True,
    ) -> None:
        """
        file = filename
        size = Override file size (useful for zero sizing links)
        """
        self._file = file
        self._stat = {}
        if file:
            try:
                if not follow_symlinks and os.path.islink(file):
                    file_stat = os.lstat(file)
                else:
                    file_stat = os.stat(file)
                self._stat['mode'] = file_stat[0]
                self._stat['inode'] = file_stat[1]
                self._stat['device'] = file_stat[2]
                self._stat['nlink'] = file_stat[3]
                self._stat['userid'] = file_stat[4]
                self._stat['groupid'] = file_stat[5]
                self._stat['size'] = file_stat[6]
                self._stat['atime'] = int(file_stat[7])
                self._stat['mtime'] = int(file_stat[8])
                self._stat['ctime'] = int(file_stat[9])
            except (OSError, TypeError) as exception:
                if not os.path.islink:
                    raise FileStatNotFoundError(
                        f"Cannot find status: {file}",
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

    def get_time_access(self) -> int:
        """
        Return time of last access
        """
        return self._stat.get('atime', 0)

    def get_time(self) -> int:
        """
        Return time of last modification
        """
        return self._stat.get('mtime', 0)

    def get_date_local(self) -> str:
        """
        Return date of last modification in ISO local date format
        (ie '2011-12-31')
        """
        return time.strftime('%Y-%m-%d', time.localtime(self.get_time()))

    def get_time_local(self) -> str:
        """
        Return time of last modification in full ISO local time format
        (ie '2011-12-31-12:30:28')
        """
        return time.strftime(
            '%Y-%m-%d-%H:%M:%S', time.localtime(self.get_time()))

    def get_time_change(self) -> int:
        """
        Return time of last meta data change.
        """
        return self._stat.get('ctime', 0)


class FileUtil:
    """
    This class contains file utilites.
    """

    @staticmethod
    def newest(files: List[str]) -> str:
        """
        Return newest file or directory.

        files = List of files
        """

        files = [x for x in files if not os.path.islink(x)]

        nfile = ''
        nfile_time = -1.
        for file in files:
            file_time = os.path.getmtime(file)
            if file_time > nfile_time:
                nfile = file
                nfile_time = file_time

        return nfile

    @staticmethod
    def oldest(files: List[str]) -> str:
        """
        Return oldest file or directory.

        files = List of files
        """
        files = [x for x in files if not os.path.islink(x)]

        nfile = ''
        nfile_time = float('inf')
        for file in files:
            file_time = os.path.getmtime(file)
            if file_time < nfile_time:
                nfile = file
                nfile_time = file_time

        return nfile

    @staticmethod
    def strings(file: str, pattern: str) -> str:
        """
        Return first match of pattern in binary file
        """
        is_match = re.compile(pattern)
        try:
            with open(file, 'rb') as ifile:
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
    def tmpdir(name: str = None) -> str:
        """
        Return temporary directory with prefix and set permissions.
        """
        tmpdir = os.path.join('/tmp', getpass.getuser())
        if name:
            directory = os.path.join(tmpdir, name)
        else:
            directory = tmpdir

        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as exception:
                raise FileTmpdirCreationError(
                    f'Cannot create directory: {tmpdir}',
                ) from exception

        try:
            os.chmod(tmpdir, int('700', 8))
        except OSError as exception:
            raise FileTmpdirPermissionError(
                f'Permission error: {tmpdir}',
            ) from exception

        return directory


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
