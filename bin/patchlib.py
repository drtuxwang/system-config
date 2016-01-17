#!/usr/bin/env python3
"""
Patch library module for modifying Python objects & class object generators
"""

import collections
import io
import os
import sys
import unittest.mock

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Patcher(object):
    """
    This class patches Python objects and class object generators.

    self._testCase = TestCase class object
    """

    def __init__(self, testCase):
        """
        testCase = TestCase class object
        """
        self._testCase = testCase

        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

        self._stderr = sys.stderr
        sys.stderr = io.StringIO()

    def __del__(self):
        if type(sys.stdout) == 'io.StringIO':
            print(sys.stdout.getvalue(), end='', file=sys.stdout)
            sys.stdout = self._stdout

        if type(sys.stderr) == 'io.StringIO':
            print(sys.stderr.getvalue(), end='', file=sys.stderr)
            sys.stderr = self._stderr

    def set_dict(self, handle, dictionary):
        """
        Patch dictionary value

        handle     = Dictionary object handle
        dictionary = Dictionary of changes
        """
        patcher = unittest.mock.patch.dict(handle, dictionary)
        patcher.start()
        self._testCase.addCleanup(patcher.stop)

    def set_file(self, file, data):
        """
        Create temp file.

        file = File name
        data = Binary data
        """
        Patch_File(self._testCase).create(file, data)

    def set_method(self, handle, method, mock=None):
        """
        Patch method of object or class object generator method

        handle = Object or class object generator handle
        method = Method name
        mock   = Return value or reference to mocked method
        """
        if isinstance(mock, collections.Callable):
            patcher = unittest.mock.patch.object(handle, method, side_effect=mock)
        else:
            patcher = unittest.mock.patch.object(handle, method, return_value=mock)
        patcher.start()
        self._testCase.addCleanup(patcher.stop)

    def set_system(self, system):
        """
        Patch Python built-in objects to pretend to be another operating system.

        system = Operating System (ie 'linux', 'windows')
        """
        Patch_os(self._testCase).set_system(system)


class Patch_File(object):
    """
    This class patches file system with a temp file.

    self._testCase = TestCase class object
    """

    def __init__(self, testCase):
        """
        testCase = TestCase class object
        """
        self._testCase = testCase

    def create(self, file, data):
        """
        Create temp file.

        file = File name
        data = Binary data
        """
        self._file = file
        self._testCase.addCleanup(self._delete)

        with open(file, 'wb') as ofile:
            ofile.write(data)

    def _delete(self):
        try:
            os.remove(self._file)
        except OSError:
            pass


class Patch_os(object):
    """
    This class patches Python built-in 'os' module objects.

    self._testCase = TestCase class object
    """

    def __init__(self, testCase):
        """
        testCase = TestCase class object
        """
        self._testCase = testCase

    def set_system(self, system):
        """
        Patch Pythion built-in 'os' module object to pretend to be another operating system

        system = Operating System (ie 'linux', 'windows')
        """

        self._os_sep = os.sep
        self._os_pathsep = os.pathsep
        self._os_path_pathsep = os.path.pathsep

        if system == 'linux':
            os.sep = '/'
            os.pathsep = ':'
            os.path.pathsep = ':'
        elif system == 'windows':
            os.sep = '\\'
            os.pathsep = ';'
            os.path.pathsep = ';'
        self._testCase.addCleanup(self._unsetSystem)

        patcher = unittest.mock.patch.object(os.path, 'join', side_effect=self.mocked_os_path_join)
        patcher.start()
        self._testCase.addCleanup(patcher.stop)

    def mocked_os_path_join(self, *args):
        """
        Mocked 'os.path.join()' pretending to be another operating system.
        """
        return os.sep.join(args)

    def _unset_system(self):
        if os.sep != self._os_sep:
            os.sep = self._os_sep

        if os.pathsep != self._os_pathsep:
            os.pathsep = self._os_pathsep

        if os.path.pathsep != self._os_path_pathsep:
            os.path.pathsep = self._os_path_pathsep


if __name__ == '__main__':
    help(__name__)
