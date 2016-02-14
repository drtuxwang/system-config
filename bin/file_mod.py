#!/usr/bin/env python3
"""
Python file handling utility module

Copyright GPL v2: 2006-2016 By Dr Colin Kong

Version 2.0.0 (2016-02-08)
"""

import os
import sys
import time

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


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
                        sys.argv[0] + ': Cannot find "' + file + '" file status.')
                self._stat = [0] * 10
            else:
                if size is not None:
                    self._stat[6] = size

    @staticmethod
    def newest(files):
        """
        Return newest file or directory.

        files = List of files
        """
        nfile_stat = None
        nfile = ''
        for file in files:
            if os.path.isfile(file) or os.path.isdir(file):
                if nfile:
                    file_stat = FileStat(file)
                    if file_stat.get_time() > nfile_stat.get_time():
                        nfile = file
                        nfile_stat = file_stat
                else:
                    nfile = file
                    nfile_stat = FileStat(nfile)
        return nfile

    @staticmethod
    def oldest(files):
        """
        Return oldest file or directory.

        files = List of files
        """
        nfile_stat = None
        nfile = ''
        for file in files:
            if os.path.isfile(file) or os.path.isdir(file):
                if nfile:
                    file_stat = FileStat(file)
                    if file_stat.get_time() < nfile_stat.get_time():
                        nfile = file
                        nfile_stat = file_stat
                else:
                    nfile = file
                    nfile_stat = FileStat(nfile)
        return nfile

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

    def get_time_local(self):
        """
        Return time of last modification in full ISO local time format (ie '2011-12-31-12:30:28')
        """
        return time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(self.get_time()))

    def get_time_create(self):
        """
        Return time of creation.
        """
        return self._stat[9]


class FileStatNotFoundError(SystemExit):
    """
    File stat not found error class.

    self.args = Arguments
    """

    def __init__(self, message):
        """
        message = Error message
        """
        super().__init__()
        self.args = (message,)

    def get_args(self):
        """
        Return arguments
        """
        return self.args


if __name__ == '__main__':
    help(__name__)
