#!/usr/bin/env python3
"""
Mock module for 'pyld.py' module
"""

import sys
import unittest.mock

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Mock_Options(unittest.mock.MagicMock):
    """
    This class mocks Options class.
    """

    def mock_get_dump_flag(self, dumpFlag):
        self.get_dump_flag = unittest.mock.MagicMock(return_value=dumpFlag)

    def mock_get_module(self, module):
        self.get_module = unittest.mock.MagicMock(return_value=module)

    def mock_get_module_args(self, args):
        self.get_module_args = unittest.mock.MagicMock(return_value=args)

    def mock_get_module_dir(self, directory):
        self.get_module_dir = unittest.mock.MagicMock(return_value=directory)

    def mock_get_library_path(self, libraryPath):
        self.get_library_path = unittest.mock.MagicMock(return_value=libraryPath)

    def mock_get_verbose_flag(self, verboseFlag):
        self.get_verbose_flag = unittest.mock.MagicMock(return_value=verboseFlag)


if __name__ == '__main__':
    help(__name__)
