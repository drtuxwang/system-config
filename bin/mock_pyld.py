#!/usr/bin/env python3
"""
Mock module for "pyld.py" module
"""

import sys
if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import unittest.mock


class Mock_Options(unittest.mock.MagicMock):
    """
    This class mocks Options class.
    """

    def mock_getDumpFlag(self, dumpFlag):
        self.getDumpFlag = unittest.mock.MagicMock(return_value=dumpFlag)

    def mock_getModule(self, module):
        self.getModule = unittest.mock.MagicMock(return_value=module)

    def mock_getModuleArgs(self, args):
        self.getModuleArgs = unittest.mock.MagicMock(return_value=args)

    def mock_getModuleDir(self, directory):
        self.getModuleDir = unittest.mock.MagicMock(return_value=directory)

    def mock_getLibraryPath(self, libraryPath):
        self.getLibraryPath = unittest.mock.MagicMock(return_value=libraryPath)

    def mock_getVerboseFlag(self, verboseFlag):
        self.getVerboseFlag = unittest.mock.MagicMock(return_value=verboseFlag)


if __name__ == "__main__":
    help(__name__)
