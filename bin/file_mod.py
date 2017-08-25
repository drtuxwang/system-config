#!/usr/bin/env python3
"""
Python file handling utility module

Copyright GPL v2: 2006-2017 By Dr Colin Kong
"""

import os
import re
import sys
import time
import yaml

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '3.0.0'
VERSION = 20170825


class FileMap(object):
    """
    This class deals with mapping apps file to extensions.
    """
    def __init__(self):
        file = os.path.join(os.path.dirname(__file__), 'file_mod.yaml')
        with open(file) as ifile:
            mappings = yaml.load(ifile)
        self._apps = mappings['apps']
        self._bindings = mappings['bindings']

    def get_app(self, app_name, view=False):
        """
        Return (command, daemon_flag) or None
        """
        app = self._apps.get(app_name)
        if app_name:
            command = app['command']
            if view and 'view_flag' in app:
                command.append(app['view_flag'])
            daemon = app.get('daemon') is True
            return (command, daemon)

        return None

    def get_open_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('open')
        if app_name:
            return self.get_app(app_name)

        return None

    def get_view_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('view')
        if app_name:
            return self.get_app(app_name, view=True)

        return None


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
