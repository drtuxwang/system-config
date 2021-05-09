#!/usr/bin/env python3
"""
Test module for 'pyld.py' module
"""

import os
import sys
import unittest
import unittest.mock
from typing import List

import pyld


class TestOptions(
    unittest.TestCase,
):  # pylint: disable = too-many-public-methods
    """
    This class tests Options class.
    """

    def setUp(self) -> None:
        """
        Setup test harness.
        """
        self.maxDiff = None  # pylint: disable = invalid-name

    @staticmethod
    def test_dump() -> None:
        """
        Test object dumping does not fail.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)
        options.dump()

    def test_get_dump_flag_default(self) -> None:
        """
        Test default dumpFlag.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_dump_flag()
        self.assertFalse(result)

    def test_get_dump_flag_pyldv(self) -> None:
        """
        Test '-pyldv' does not set dumpFlag.
        """
        args = ['arg0', 'moduleX', '-pyldv']
        options = pyld.Options(args)

        result = options.get_dump_flag()
        self.assertFalse(result)

    def test_get_dump_flag_pyldverbose(self) -> None:
        """
        Test '-pyldverbose' does not set dumpFlag.
        """
        args = ['arg0', 'moduleX', '-pyldverbose']
        options = pyld.Options(args)

        result = options.get_dump_flag()
        self.assertFalse(result)

    def test_get_dump_flag_pyldvv(self) -> None:
        """
        Test '-pyldvv' sets dump flag.
        """
        args = ['arg0', 'moduleX', '-pyldvv']
        options = pyld.Options(args)

        result = options.get_dump_flag()
        self.assertTrue(result)

    def test_get_dump_flag_pyldvvv(self) -> None:
        """
        Test '-pyldvvv' sets dump flag.
        """
        args = ['arg0', 'moduleX', '-pyldvvv']
        options = pyld.Options(args)

        result = options.get_dump_flag()
        self.assertTrue(result)

    def test_get_library_path_default(self) -> None:
        """
        Test default library path.
        """
        expected: List[str] = []
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_library_path()
        self.assertListEqual(result, expected)

    def test_get_library_path_pyldpath(self) -> None:
        """
        Test '-pyldpath libpath1:libpath2' sets library path.
        """
        expected = ['pathX', 'pathY']
        args = [
            'arg0',
            'moduleX',
            '-pyldpath',
            'pathX' + os.path.pathsep + 'pathY'
        ]
        options = pyld.Options(args)

        result = options.get_library_path()
        self.assertListEqual(result, expected)

    def test_get_library_path_pyldpath_error(self) -> None:
        """
        Test '-pyldpath' without 2nd argument raise exception and
        exit status 2.
        """
        expected = (
            os.path.basename(sys.argv[0]) +
            ': error: argument -pyldpath: expected 1 argument'
        )
        args = ['arg0', 'moduleX', '-pyldpath', '-pyldv']

        with self.assertRaises(SystemExit) as context:
            pyld.Options(args)
        self.assertEqual(2, context.exception.args[0])

        # pylint: disable = no-member
        result = pyld.sys.stderr.getvalue()  # type: ignore
        self.assertIn(expected, result)

    def test_get_module(self) -> None:
        """
        Test module name is passed correctly.
        """
        expected = 'moduleX'
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_module()
        self.assertEqual(result, expected)

    def test_get_module_name_default(self) -> None:
        """
        Test getting module name default.
        """
        expected = 'moduleX'
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_module_name()
        self.assertEqual(result, expected)

    def test_get_module_name_pyldname1(self) -> None:
        """
        Test '-pyldname moduleY' sets module name.
        """
        expected = 'moduleY'
        args = ['arg0', '-pyldname', 'moduleY', 'moduleX']
        options = pyld.Options(args)

        result = options.get_module_name()
        self.assertEqual(result, expected)

    def test_get_module_name_pyldname2(self) -> None:
        """
        Test '-pyldname=moduleY' sets module name.
        """
        expected = 'moduleY'
        args = ['arg0', '-pyldname=moduleY', 'moduleX']
        options = pyld.Options(args)

        result = options.get_module_name()
        self.assertEqual(result, expected)

    def test_get_module_args_default(self) -> None:
        """
        Test module arguments default is empty.
        """
        expected: List[str] = []
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_result(self) -> None:
        """
        Test module arguments are passed correctly.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = ['arg0', 'moduleX', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_pyldpath(self) -> None:
        """
        Test that '-pyldpath' does not get passed into module arguments.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = [
            'arg0',
            'moduleX',
            '-pyldpath',
            'pathX' + os.path.pathsep + 'pathY',
            'moduleYarg1',
            'moduleYarg2'
        ]
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_pyldv(self) -> None:
        """
        Test that '-pyldv' does not get passed into module arguments.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = ['arg0', 'moduleX', '-pyldv', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_pyldverbose(self) -> None:
        """
        Test that '-pyldverbose' does not get passed into module arguments.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = [
            'arg0',
            'moduleX',
            '-pyldverbose',
            'moduleYarg1',
            'moduleYarg2'
        ]
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_pyldvv(self) -> None:
        """
        Test that '-pyldvv' does not get passed into module arguments.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = ['arg0', 'moduleX', '-pyldvv', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_modules_args_pyldvvv(self) -> None:
        """
        Test that '-pyldvvv' does not get passed into module arguments.
        """
        expected = ['moduleYarg1', 'moduleYarg2']
        args = [
            'arg0',
            'moduleX',
            '-pyldvvv',
            'moduleYarg1',
            'moduleYarg2'
        ]
        options = pyld.Options(args)

        result = options.get_module_args()
        self.assertListEqual(result, expected)

    def test_get_module_dir_result(self) -> None:
        """
        Test module directory is correctly detected.
        """
        expected = 'myDir'
        args = [
            os.path.join('myDir', 'myFile'),
            os.path.join('moduleDir', 'moduleX')
        ]
        options = pyld.Options(args)

        result = options.get_module_dir()
        self.assertEqual(result, expected)

    def test_get_verbose_flag_default(self) -> None:
        """
        Test verbose flag default.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        result = options.get_verbose_flag()
        self.assertFalse(result)

    def test_get_verbose_flag_pyldv(self) -> None:
        """
        Test '-pyldv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldv']
        options = pyld.Options(args)

        result = options.get_verbose_flag()
        self.assertTrue(result)

    def test_get_verbose_flag_pyldverbose(self) -> None:
        """
        Test '-pyldverbose' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldverbose']
        options = pyld.Options(args)

        result = options.get_verbose_flag()
        self.assertTrue(result)

    def test_get_verbose_flag_pyldvv(self) -> None:
        """
        Test '-pyldvv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldvv']
        options = pyld.Options(args)

        result = options.get_verbose_flag()
        self.assertTrue(result)

    def test_get_verbose_flag_pyldvvv(self) -> None:
        """
        Test '-pyldvvv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldvvv']
        options = pyld.Options(args)

        result = options.get_verbose_flag()
        self.assertTrue(result)

    def test_help_h(self) -> None:
        """
        Test '-h' displays help.
        """
        all_expected = ('positional arguments:', 'optional arguments:')
        args = ['arg0', '-h']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        # pylint: disable = no-member
        result = pyld.sys.stdout.getvalue()  # type: ignore
        for expected in all_expected:
            self.assertIn(expected, result)

    def test_help_help(self) -> None:
        """
        Test '--h' displays help.
        """
        all_expected = ('positional arguments:', 'optional arguments:')
        args = ['arg0', '--h']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        # pylint: disable = no-member
        result = pyld.sys.stdout.getvalue()  # type: ignore
        for expected in all_expected:
            self.assertIn(expected, result)

    def test_help_help2(self) -> None:
        """
        Test '--help' displays help.
        """
        all_expected = ('positional arguments:', 'optional arguments:')
        args = ['arg0', '--help']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        # pylint: disable = no-member
        result = pyld.sys.stdout.getvalue()  # type: ignore
        for expected in all_expected:
            self.assertIn(expected, result)

    def test_init_flags_none(self) -> None:
        """
        Test argparse error exit status 2 when no arguments are
        supplied.
        """
        expected = (
            os.path.basename(sys.argv[0]) +
            ': error: the following arguments are required: module, arg'
        )
        args = ['arg0']

        with self.assertRaises(SystemExit) as context:
            pyld.Options(args)

        self.assertEqual(2, context.exception.args[0])

        # pylint: disable = no-member
        result = pyld.sys.stderr.getvalue()  # type: ignore
        self.assertIn(expected, result)


class TestPythonLoader(unittest.TestCase):
    """
    This class tests PythonLoader class.
    """

    def setUp(self) -> None:
        """
        Setup test harness.
        """
        self.maxDiff = None  # pylint: disable = invalid-name
        self._start_directory = os.getcwd()
        os.chdir(os.path.dirname(__file__))

        self._mock_options = unittest.mock.MagicMock('mock_options')
        self._mock_options.get_dump_flag = unittest.mock.MagicMock(
            return_value=False)
        self._mock_options.get_library_path = unittest.mock.MagicMock(
            return_value=[])
        self._mock_options.get_module = unittest.mock.MagicMock(
            return_value='arg0')
        self._mock_options.get_module_name = unittest.mock.MagicMock(
            return_value='arg0')
        self._mock_options.get_module_args = unittest.mock.MagicMock(
            return_value=['args1', 'args2'])
        self._mock_options.get_module_dir = unittest.mock.MagicMock(
            return_value='directory')
        self._mock_options.get_verbose_flag = unittest.mock.MagicMock(
            return_value=False)
        self._mock_options.dump = unittest.mock.MagicMock()

    def tearDown(self) -> None:
        os.chdir(self._start_directory)

    @unittest.mock.patch('pyld.PythonLoader.dump', return_value=None)
    def test_dump(self, _: unittest.mock.MagicMock) -> None:
        """
        Test object dumping does not fail.
        """
        python_loader = pyld.PythonLoader(self._mock_options)
        python_loader.dump()

        # pylint: disable = no-member
        self.assertTrue(python_loader.dump.called)  # type: ignore

    @unittest.mock.patch('pyld.PythonLoader.dump', return_value=None)
    def test_run_dump_flag(self, _: unittest.mock.MagicMock) -> None:
        """
        Test run with dump flag set.
        """
        self._mock_options.get_dump_flag = unittest.mock.MagicMock(
            return_value=True)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

        # pylint: disable = no-member
        self.assertTrue(python_loader.dump.called)  # type: ignore

    def test_run_import_error(self) -> None:
        """
        Test run failure when module does not exist
        """
        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

    def test_run_import_main(self) -> None:
        """
        Test run loads module and calls 'Main()'.
        We use this module as the test module.
        """
        self._mock_options.get_module = unittest.mock.MagicMock(
            return_value='test_pyld')
        self._mock_options.get_module_dir = unittest.mock.MagicMock(
            return_value=os.curdir)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(AttributeError) as context:
            python_loader.run()

        self.assertIn("has no attribute 'Main'", context.exception.args[0])

    def test_run_library_path(self) -> None:
        """
        Test run with '-libpath' sets Python system path.
        """
        self._mock_options.get_library_path = unittest.mock.MagicMock(
            return_value=['directory1', 'directory2'])

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()
        self.assertIn('directory1', sys.path)
        self.assertIn('directory2', sys.path)

    def test_run_pyldverbose_flag(self) -> None:
        """
        Test run with '-pyldverbose' flag on.
        """
        self._mock_options.get_verbose_flag = unittest.mock.MagicMock(
            return_value=True)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

        # pylint: disable = no-member
        result = pyld.sys.stdout.getvalue()  # type: ignore
        self.assertIn('sys.argv =', result)

    def test_get_options(self) -> None:
        """
        Test options is set correctly.
        """
        python_loader = pyld.PythonLoader(self._mock_options)

        result = python_loader.get_options()
        self.assertEqual(result, self._mock_options)

    def test_get_sys_argv(self) -> None:
        """
        Test getting Python system arguments (faked by pyld).
        """
        expected = [os.path.join('directory', 'arg0'), 'args1', 'args2']

        python_loader = pyld.PythonLoader(self._mock_options)

        result: list = python_loader.get_sys_argv()
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        print("\n" + __file__ + ":unittest.main(verbosity=2, buffer=True):")
        unittest.main(verbosity=2, buffer=True)
