#!/usr/bin/env python3
"""
Python file handling utility module

Copyright GPL v2: 2006-2017 By Dr Colin Kong
"""

import os
import re
import sys
import time

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '2.2.0'
VERSION = 20170829


class FileStat(object):
    """
    This class contains file status information.

    self._file = Filename
    self._stat = [mode, ino, idev, nlink, uid, gid, size, atime, mtime, ctime]
    """

    def __init__(self, file='', size=None):
        """
        file = filename

        size = Override file size (useful for zero sizing links)
        """
        if file:
            self._file = file
            try:
                self._stat = list(os.stat(file))
            except (OSError, TypeError):
                if not os.path.islink:
                    raise FileStatNotFoundError(
                        'Cannot find "' + file + '" file status.')
                self._stat = [0] * 10
            else:
                if size is not None:
                    self._stat[6] = size

    def get_file(self):
        """
        Return filename
        """
        return self._file

    def get_mode(self):
        """
        Return inode protection mode
        """
        return self._stat[0]

    def get_inode_number(self):
        """
        Return inode number
        """
        return self._stat[1]

    def get_inode_device(self):
        """
        Return device inode resides on
        """
        return self._stat[2]

    def get_number_links(self):
        """
        Return number of links to the inode
        """
        return self._stat[3]

    def get_userid(self):
        """
        Return user ID of the owner
        """
        return self._stat[4]

    def get_groupid(self):
        """
        Return group ID of the owner
        """
        return self._stat[5]

    def get_size(self):
        """
        Return size in bytes of a file
        """
        return self._stat[6]

    def get_time_access(self):
        """
        Return time of last access
        """
        return self._stat[7]

    def get_time(self):
        """
        Return time of last modification
        """
        return self._stat[8]

    def get_date_local(self):
        """
        Return date of last modification in ISO local date format
        (ie '2011-12-31')
        """
        return time.strftime('%Y-%m-%d', time.localtime(self.get_time()))

    def get_time_local(self):
        """
        Return time of last modification in full ISO local time format
        (ie '2011-12-31-12:30:28')
        """
        return time.strftime(
            '%Y-%m-%d-%H:%M:%S', time.localtime(self.get_time()))

    def get_time_change(self):
        """
        Return time of last meta data change.
        """
        return self._stat[9]


class FileUtil(object):
    """
    This class contains file utilites.
    """

    @staticmethod
    def newest(files):
        """
        Return newest file or directory.

        files = List of files
        """

        files = [x for x in files if not os.path.islink(x)]

        nfile = ''
        nfile_time = -1
        for file in files:
            file_time = FileStat(file).get_time()
            if file_time > nfile_time:
                nfile = file
                nfile_time = file_time

        return nfile

    @staticmethod
    def oldest(files):
        """
        Return oldest file or directory.

        files = List of files
        """
        files = [x for x in files if not os.path.islink(x)]

        nfile = ''
        nfile_time = float('inf')
        for file in files:
            file_time = FileStat(file).get_time()
            if file_time < nfile_time:
                nfile = file
                nfile_time = file_time

        return nfile

    @staticmethod
    def strings(file, pattern):
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
                        if byte > 31 and byte < 127:
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


class FileError(Exception):
    """
    File module error class.
    """


class FileStatNotFoundError(FileError):
    """
    File stat not found error class.
    """


if __name__ == '__main__':
    help(__name__)
