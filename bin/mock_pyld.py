#!/usr/bin/env python3
"""
Mock module for 'pyld.py' module
"""

import sys
import unittest.mock

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class MockOptions(unittest.mock.MagicMock):
    """
    This class mocks Options class.
    """

    def __init__(self, **args):
        super().__init__(*args)
        self.get_dump_flag = unittest.mock.MagicMock()
        self.get_module = unittest.mock.MagicMock()
        self.get_module_name = unittest.mock.MagicMock()
        self.get_module_args = unittest.mock.MagicMock()
        self.get_module_dir = unittest.mock.MagicMock()
        self.get_library_path = unittest.mock.MagicMock()
        self.get_verbose_flag = unittest.mock.MagicMock()

    def mock_get_dump_flag(self, dump_flag):
        """
        Mock get dump flag
        """
        self.get_dump_flag = unittest.mock.MagicMock(return_value=dump_flag)

    def mock_get_module(self, module):
        """
        Mock get module
        """
        self.get_module = unittest.mock.MagicMock(return_value=module)

    def mock_get_module_name(self, name):
        """
        Mock get module name
        """
        self.get_module_name = unittest.mock.MagicMock(return_value=name)

    def mock_get_module_args(self, args):
        """
        Mock get module args
        """
        self.get_module_args = unittest.mock.MagicMock(return_value=args)

    def mock_get_module_dir(self, directory):
        """
        Mock get module dir
        """
        self.get_module_dir = unittest.mock.MagicMock(return_value=directory)

    def mock_get_library_path(self, library_path):
        """
        Mock get library path
        """
        self.get_library_path = unittest.mock.MagicMock(return_value=library_path)

    def mock_get_verbose_flag(self, verbose_flag):
        """
        Mock get verbose flag
        """
        self.get_verbose_flag = unittest.mock.MagicMock(return_value=verbose_flag)


if __name__ == '__main__':
    help(__name__)
