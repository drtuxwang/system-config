#!/usr/bin/env python3
"""
Test module for "pyld.py" module
"""

import sys
if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal
import unittest
import unittest.mock

import mock_pyld
import patchlib
import pyld


class Test_Options(unittest.TestCase):
    """
    This class tests Options class.
    """

    def setUp(self):
        """
        Setup test harness.
        """
        self.maxDiff = None
        self._patcher = patchlib.Patcher(self)

    def test_dump(self):
        """
        Test object dumping does not fail.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)
        options.dump("options.")

    def test_getDumpFlag_Default(self):
        """
        Test default dumpFlag.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)

        value = options.getDumpFlag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_getDumpFlag_pyldv(self):
        """
        Test "-pyldv" does not set dumpFlag.
        """
        args = ["arg0", "moduleX", "-pyldv"]
        options = pyld.Options(args)

        value = options.getDumpFlag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_getDumpFlag_pyldverbose(self):
        """
        Test "-pyldverbose" does not set dumpFlag.
        """
        args = ["arg0", "moduleX", "-pyldverbose"]
        options = pyld.Options(args)

        value = options.getDumpFlag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_getDumpFlag_pyldvv(self):
        """
        Test "-pyldvv" sets dump flag.
        """
        args = ["arg0", "moduleX", "-pyldvv"]
        options = pyld.Options(args)

        value = options.getDumpFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_getDumpFlag_pyldvvv(self):
        """
        Test "-pyldvvv" sets dump flag.
        """
        args = ["arg0", "moduleX", "-pyldvvv"]
        options = pyld.Options(args)

        value = options.getDumpFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_getLibraryPath_Default(self):
        """
        Test default library path.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)

        value = options.getLibraryPath()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [])

    def test_getLibraryPath_pyldpath(self):
        """
        Test "-pyldpath libpath1:libpath2" sets library path.
        """
        args = ["arg0", "moduleX", "-pyldpath", "pathX" + os.path.pathsep + "pathY"]
        options = pyld.Options(args)

        value = options.getLibraryPath()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["pathX", "pathY"])

    def test_getLibraryPath_pyldpathError(self):
        """
        Test "-pyldpath" without 2nd argument raise exception and exit status 2.
        """
        args = ["arg0", "moduleX", "-pyldpath", "-pyldv"]

        with self.assertRaises(SystemExit) as context:
            options = pyld.Options(args)
        self.assertIsInstance(context.exception.args, tuple)
        self.assertEqual(context.exception.args[0], 2)

        value = pyld.sys.stderr.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn(os.path.basename(sys.argv[0]) +
                      ": error: argument -pyldpath: expected 1 argument", value)

    def test_getModule_Value(self):
        """
        Test module name is passed correctly.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)

        value = options.getModule()
        self.assertIsInstance(value, str)
        self.assertEqual(value, "moduleX")

    def test_getModuleArgs_Default(self):
        """
        Test module arguments default is empty.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [])

    def test_getModulesArgs_Value(self):
        """
        Test module arguments are passed correctly.
        """
        args = ["arg0", "moduleX", "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModulesArgs_pyldpath(self):
        """
        Test that "-pyldpath" does not get passed into module arguments.
        """
        args = ["arg0", "moduleX", "-pyldpath", "pathX" + os.path.pathsep + "pathY",
                "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModulesArgs_pyldv(self):
        """
        Test that "-pyldv" does not get passed into module arguments.
        """
        args = ["arg0", "moduleX", "-pyldv", "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModulesArgs_pyldverbose(self):
        """
        Test that "-pyldverbose" does not get passed into module arguments.
        """
        args = ["arg0", "moduleX", "-pyldverbose", "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModulesArgs_pyldvv(self):
        """
        Test that "-pyldvv" does not get passed into module arguments.
        """
        args = ["arg0", "moduleX", "-pyldvv", "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModulesArgs_pyldvvv(self):
        """
        Test that "-pyldvvv" does not get passed into module arguments.
        """
        args = ["arg0", "moduleX", "-pyldvvv", "moduleYarg1", "moduleYarg2"]
        options = pyld.Options(args)

        value = options.getModuleArgs()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ["moduleYarg1", "moduleYarg2"])

    def test_getModuleDir_Value(self):
        """
        Test module directory is correctly detected.
        """
        args = [os.path.join("myDir", "myFile"), os.path.join("moduleDir", "moduleX")]
        options = pyld.Options(args)

        value = options.getModuleDir()
        self.assertIsInstance(value, str)
        self.assertEqual(value, "myDir")

    def test_getVerboseFlag_Default(self):
        """
        Test verbose flag default.
        """
        args = ["arg0", "moduleX"]
        options = pyld.Options(args)

        value = options.getVerboseFlag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_getVerboseFlag_pyldv(self):
        """
        Test "-pyldv" sets verbose flag.
        """
        args = ["arg0", "moduleX", "-pyldv"]
        options = pyld.Options(args)

        value = options.getVerboseFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_getVerboseFlag_pyldverbose(self):
        """
        Test "-pyldverbose" sets verbose flag.
        """
        args = ["arg0", "moduleX", "-pyldverbose"]
        options = pyld.Options(args)

        value = options.getVerboseFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_getVerboseFlag_pyldvv(self):
        """
        Test "-pyldvv" sets verbose flag.
        """
        args = ["arg0", "moduleX", "-pyldvv"]
        options = pyld.Options(args)

        value = options.getVerboseFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_getVerboseFlag_pyldvvv(self):
        """
        Test "-pyldvvv" sets verbose flag.
        """
        args = ["arg0", "moduleX", "-pyldvvv"]
        options = pyld.Options(args)

        value = options.getVerboseFlag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_help_h(self):
        """
        Test "-h" displays help.
        """
        args = ["arg0", "-h"]

        with self.assertRaises(SystemExit) as context:
            options = pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn("positional arguments:", value)
        self.assertIn("optional arguments:", value)

    def test_help_help(self):
        """
        Test "--h" displays help.
        """
        args = ["arg0", "--h"]

        with self.assertRaises(SystemExit) as context:
            options = pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn("positional arguments:", value)
        self.assertIn("optional arguments:", value)

    def test_help_help2(self):
        """
        Test "--help" displays help.
        """
        args = ["arg0", "--help"]

        with self.assertRaises(SystemExit) as context:
            options = pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn("positional arguments:", value)
        self.assertIn("optional arguments:", value)

    def test_init_FlagsNone(self):
        """
        Test argparse error exit status 2 when no arguments are supplied.
        """
        args = ["arg0"]

        with self.assertRaises(SystemExit) as context:
            options = pyld.Options(args)
        self.assertIsInstance(context.exception.args, tuple)
        self.assertEqual(context.exception.args[0], 2)

        value = pyld.sys.stderr.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn(os.path.basename(sys.argv[0]) +
                      ": error: the following arguments are required: module, arg", value)


class Test_PythonLoader(unittest.TestCase):
    """
    This class tests PythonLoader class.
    """

    def setUp(self):
        """
        Setup test harness.
        """
        self.maxDiff = None
        self._patcher = patchlib.Patcher(self)

        self._options = mock_pyld.Mock_Options()
        self._options.mock_getDumpFlag(False)
        self._options.mock_getLibraryPath([])
        self._options.mock_getModule("arg0")
        self._options.mock_getModuleArgs(["args1", "args2"])
        self._options.mock_getModuleDir("directory")
        self._options.mock_getVerboseFlag(False)

    def test_dump(self):
        """
        Test object dumping does not fail.
        """
        pythonLoader = pyld.PythonLoader(self._options)
        pythonLoader.dump("pythonLoader.")

    def test_run_dumpFlag(self):
        """
        Test run with dump flag set.
        """
        self._patcher.setMethod(pyld.PythonLoader, "dump")
        self._options.mock_getDumpFlag(True)

        pythonLoader = pyld.PythonLoader(self._options)

        with self.assertRaises(ImportError) as context:
            pythonLoader.run()

        self.assertTrue(pythonLoader.dump.called)

    def test_run_importError(self):
        """
        Test run failure when module does not exist
        """
        pythonLoader = pyld.PythonLoader(self._options)

        with self.assertRaises(ImportError) as context:
            pythonLoader.run()

    def test_run_importMain(self):
        """
        Test run loads module and calls "Main()". We use this module as the tets module.
        """
        self._options.mock_getModule("test_pyld")

        pythonLoader = pyld.PythonLoader(self._options)

        with self.assertRaises(AttributeError) as context:
            pythonLoader.run()
        self.assertIsInstance(context.exception.args, tuple)
        self.assertIn("has no attribute 'Main'", context.exception.args[0])

    def test_run_libraryPath(self):
        """
        Test run with "-libpath" sets Python system path.
        """
        self._options.mock_getLibraryPath(["directory1", "directory2"])

        pythonLoader = pyld.PythonLoader(self._options)

        with self.assertRaises(ImportError) as context:
            pythonLoader.run()
        self.assertIn("directory1", sys.path)
        self.assertIn("directory2", sys.path)

    def test_run_pyldverboseFlag(self):
        """
        Test run with "-pyldverbose" flag on.
        """
        self._options.mock_getVerboseFlag(True)

        pythonLoader = pyld.PythonLoader(self._options)

        with self.assertRaises(ImportError) as context:
            pythonLoader.run()

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn("sys.argv =", value)

    def test_getOptions(self):
        """
        Test options is set correctly.
        """
        pythonLoader = pyld.PythonLoader(self._options)

        value = pythonLoader.getOptions()
        self.assertIsInstance(value, unittest.mock.MagicMock)
        self.assertEqual(value, self._options)

    def test_getSysArgv(self):
        """
        Test getting Python system arguments (faked by pyld).
        """
        pythonLoader = pyld.PythonLoader(self._options)

        value = pythonLoader.getSysArgv()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [os.path.join("directory", "arg0.py"), "args1", "args2"])


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        print('\n' + __file__ + ':unittest.main(verbosity=2, buffer=True):')
        unittest.main(verbosity=2, buffer=True)
