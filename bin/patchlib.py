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


class Patcher(object):
    """
    This class patches Python objects and class object generators.

    self._test_case = TestCase class object
    """

    def __init__(self, test_case):
        """
        test_case = TestCase class object
        """
        self._test_case = test_case

        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

        self._stderr = sys.stderr
        sys.stderr = io.StringIO()

    def __del__(self):
        if isinstance(sys.stdout, io.StringIO):
            print(sys.stdout.getvalue(), end='', file=sys.stdout)
            sys.stdout = self._stdout

        if isinstance(sys.stderr, io.StringIO):
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
        self._test_case.addCleanup(patcher.stop)

    def set_file(self, file, data):
        """
        Create temp file.

        file = File name
        data = Binary data
        """
        PatchFile(self._test_case).create(file, data)

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
        self._test_case.addCleanup(patcher.stop)

    def set_system(self, system):
        """
        Patch Python built-in objects to pretend to be another operating system.

        system = Operating System (ie 'linux', 'windows')
        """
        PatchOs(self._test_case).set_system(system)


class PatchFile(object):
    """
    This class patches file system with a temp file.

    self._test_case = TestCase class object
    """

    def __init__(self, test_case):
        """
        test_case = TestCase class object
        """
        self._test_case = test_case
        self._tmpfiles = []

    def create(self, file, data):
        """
        Create temp file.

        file = File name
        data = Binary data
        """
        self._tmpfiles.append(file)
        self._test_case.addCleanup(self._delete)

        with open(file, 'wb') as ofile:
            ofile.write(data)

    @staticmethod
    def remove(file):
        """
        Remove file
        """
        try:
            os.remove(file)
        except OSError:
            pass

    def _delete(self):
        for file in self._tmpfiles:
            self.remove(file)


class PatchOs(object):
    """
    This class patches Python built-in 'os' module objects.

    self._test_case = TestCase class object
    """

    def __init__(self, test_case):
        """
        test_case = TestCase class object
        """
        self._test_case = test_case
        self._info = {}

    def set_system(self, system):
        """
        Patch Pythion built-in 'os' module object to pretend to be another operating system

        system = Operating System (ie 'linux', 'windows')
        """

        self._info['os.sep'] = os.sep
        self._info['os.pathsep'] = os.pathsep
        self._info['os.path.pathsep'] = os.path.pathsep

        if system == 'linux':
            os.sep = '/'
            os.pathsep = ':'
            os.path.pathsep = ':'
        elif system == 'windows':
            os.sep = '\\'
            os.pathsep = ';'
            os.path.pathsep = ';'
        self._test_case.addCleanup(self._unset_system)

        patcher = unittest.mock.patch.object(os.path, 'join', side_effect=self.mocked_os_path_join)
        patcher.start()
        self._test_case.addCleanup(patcher.stop)

    @staticmethod
    def mocked_os_path_join(*args):
        """
        Mocked 'os.path.join()' pretending to be another operating system.
        """
        return os.sep.join(args)

    def _unset_system(self):
        if os.sep != self._info['os.sep']:
            os.sep = self._info['os.sep']

        if os.pathsep != self._info['os.pathsep']:
            os.pathsep = self._info['os.pathsep']

        if os.path.pathsep != self._info['os.path.pathsep']:
            os.path.pathsep = self._info['os.path.pathsep']


if __name__ == '__main__':
    help(__name__)
