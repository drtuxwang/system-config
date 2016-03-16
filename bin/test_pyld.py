#!/usr/bin/env python3
"""
Test module for 'pyld.py' module
"""

import os
import sys
import unittest
import unittest.mock

import pyld

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable = invalid-name, no-member, too-many-public-methods


class TestOptions(unittest.TestCase):
    """
    This class tests Options class.
    """

    def setUp(self):
        """
        Setup test harness.
        """
        self.maxDiff = None

    @staticmethod
    def test_dump():
        """
        Test object dumping does not fail.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)
        options.dump()

    def test_get_dump_flag_default(self):
        """
        Test default dumpFlag.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_dump_flag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_get_dump_flag_pyldv(self):
        """
        Test '-pyldv' does not set dumpFlag.
        """
        args = ['arg0', 'moduleX', '-pyldv']
        options = pyld.Options(args)

        value = options.get_dump_flag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_get_dump_flag_pyldverbose(self):
        """
        Test '-pyldverbose' does not set dumpFlag.
        """
        args = ['arg0', 'moduleX', '-pyldverbose']
        options = pyld.Options(args)

        value = options.get_dump_flag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_get_dump_flag_pyldvv(self):
        """
        Test '-pyldvv' sets dump flag.
        """
        args = ['arg0', 'moduleX', '-pyldvv']
        options = pyld.Options(args)

        value = options.get_dump_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_get_dump_flag_pyldvvv(self):
        """
        Test '-pyldvvv' sets dump flag.
        """
        args = ['arg0', 'moduleX', '-pyldvvv']
        options = pyld.Options(args)

        value = options.get_dump_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_get_library_path_default(self):
        """
        Test default library path.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_library_path()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [])

    def test_get_library_path_pyldpath(self):
        """
        Test '-pyldpath libpath1:libpath2' sets library path.
        """
        args = ['arg0', 'moduleX', '-pyldpath', 'pathX' + os.path.pathsep + 'pathY']
        options = pyld.Options(args)

        value = options.get_library_path()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['pathX', 'pathY'])

    def test_get_library_path_pyldpath_error(self):
        """
        Test '-pyldpath' without 2nd argument raise exception and exit status 2.
        """
        args = ['arg0', 'moduleX', '-pyldpath', '-pyldv']

        with self.assertRaises(SystemExit) as context:
            pyld.Options(args)
        self.assertIsInstance(context.exception.args, tuple)
        self.assertEqual(2, context.exception.args[0])

        value = pyld.sys.stderr.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn(os.path.basename(sys.argv[0]) +
                      ': error: argument -pyldpath: expected 1 argument', value)

    def test_get_module(self):
        """
        Test module name is passed correctly.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_module()
        self.assertIsInstance(value, str)
        self.assertEqual(value, 'moduleX')

    def test_get_module_name_default(self):
        """
        Test getting module name default.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_module_name()
        self.assertIsInstance(value, str)
        self.assertEqual(value, 'moduleX')

    def test_get_module_name_pyldname1(self):
        """
        Test '-pyldname moduleY' sets module name.
        """
        args = ['arg0', '-pyldname', 'moduleY', 'moduleX']
        options = pyld.Options(args)

        value = options.get_module_name()
        self.assertIsInstance(value, str)
        self.assertEqual(value, 'moduleY')

    def test_get_module_name_pyldname2(self):
        """
        Test '-pyldname=moduleY' sets module name.
        """
        args = ['arg0', '-pyldname=moduleY', 'moduleX']
        options = pyld.Options(args)

        value = options.get_module_name()
        self.assertIsInstance(value, str)
        self.assertEqual(value, 'moduleY')

    def test_get_module_args_default(self):
        """
        Test module arguments default is empty.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [])

    def test_get_modules_args_value(self):
        """
        Test module arguments are passed correctly.
        """
        args = ['arg0', 'moduleX', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_modules_args_pyldpath(self):
        """
        Test that '-pyldpath' does not get passed into module arguments.
        """
        args = ['arg0', 'moduleX', '-pyldpath', 'pathX' + os.path.pathsep + 'pathY',
                'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_modules_args_pyldv(self):
        """
        Test that '-pyldv' does not get passed into module arguments.
        """
        args = ['arg0', 'moduleX', '-pyldv', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_modules_args_pyldverbose(self):
        """
        Test that '-pyldverbose' does not get passed into module arguments.
        """
        args = ['arg0', 'moduleX', '-pyldverbose', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_modules_args_pyldvv(self):
        """
        Test that '-pyldvv' does not get passed into module arguments.
        """
        args = ['arg0', 'moduleX', '-pyldvv', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_modules_args_pyldvvv(self):
        """
        Test that '-pyldvvv' does not get passed into module arguments.
        """
        args = ['arg0', 'moduleX', '-pyldvvv', 'moduleYarg1', 'moduleYarg2']
        options = pyld.Options(args)

        value = options.get_module_args()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, ['moduleYarg1', 'moduleYarg2'])

    def test_get_module_dir_value(self):
        """
        Test module directory is correctly detected.
        """
        args = [os.path.join('myDir', 'myFile'), os.path.join('moduleDir', 'moduleX')]
        options = pyld.Options(args)

        value = options.get_module_dir()
        self.assertIsInstance(value, str)
        self.assertEqual('myDir', value)

    def test_get_verbose_flag_default(self):
        """
        Test verbose flag default.
        """
        args = ['arg0', 'moduleX']
        options = pyld.Options(args)

        value = options.get_verbose_flag()
        self.assertIsInstance(value, bool)
        self.assertFalse(value)

    def test_get_verbose_flag_pyldv(self):
        """
        Test '-pyldv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldv']
        options = pyld.Options(args)

        value = options.get_verbose_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_get_verbose_flag_pyldverbose(self):
        """
        Test '-pyldverbose' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldverbose']
        options = pyld.Options(args)

        value = options.get_verbose_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_get_verbose_flag_pyldvv(self):
        """
        Test '-pyldvv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldvv']
        options = pyld.Options(args)

        value = options.get_verbose_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_get_verbose_flag_pyldvvv(self):
        """
        Test '-pyldvvv' sets verbose flag.
        """
        args = ['arg0', 'moduleX', '-pyldvvv']
        options = pyld.Options(args)

        value = options.get_verbose_flag()
        self.assertIsInstance(value, bool)
        self.assertTrue(value)

    def test_help_h(self):
        """
        Test '-h' displays help.
        """
        args = ['arg0', '-h']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn('positional arguments:', value)
        self.assertIn('optional arguments:', value)

    def test_help_help(self):
        """
        Test '--h' displays help.
        """
        args = ['arg0', '--h']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn('positional arguments:', value)
        self.assertIn('optional arguments:', value)

    def test_help_help2(self):
        """
        Test '--help' displays help.
        """
        args = ['arg0', '--help']

        with self.assertRaises(SystemExit):
            pyld.Options(args)

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn('positional arguments:', value)
        self.assertIn('optional arguments:', value)

    def test_init_flags_none(self):
        """
        Test argparse error exit status 2 when no arguments are supplied.
        """
        args = ['arg0']

        with self.assertRaises(SystemExit) as context:
            pyld.Options(args)

        self.assertIsInstance(context.exception.args, tuple)
        self.assertEqual(2, context.exception.args[0])

        value = pyld.sys.stderr.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn(os.path.basename(sys.argv[0]) +
                      ': error: the following arguments are required: module, arg', value)


class TestPythonLoader(unittest.TestCase):
    """
    This class tests PythonLoader class.
    """

    def setUp(self):
        """
        Setup test harness.
        """
        self.maxDiff = None
        self._start_directory = os.getcwd()
        os.chdir(os.path.dirname(__file__))

        self._mock_options = unittest.mock.MagicMock('mock_options')
        self._mock_options.get_dump_flag = unittest.mock.MagicMock(return_value=False)
        self._mock_options.get_library_path = unittest.mock.MagicMock(return_value=[])
        self._mock_options.get_module = unittest.mock.MagicMock(return_value='arg0')
        self._mock_options.get_module_name = unittest.mock.MagicMock(return_value='arg0')
        self._mock_options.get_module_args = unittest.mock.MagicMock(
            return_value=['args1', 'args2'])
        self._mock_options.get_module_dir = unittest.mock.MagicMock(return_value='directory')
        self._mock_options.get_verbose_flag = unittest.mock.MagicMock(return_value=False)
        self._mock_options.dump = unittest.mock.MagicMock()

    def tearDown(self):
        os.chdir(self._start_directory)

    def test_dump(self):
        """
        Test object dumping does not fail.
        """
        patch_dump = unittest.mock.patch.object(pyld.PythonLoader, 'dump', return_value=None)
        patch_dump.start()

        python_loader = pyld.PythonLoader(self._mock_options)
        python_loader.dump()

        self.assertTrue(python_loader.dump.called)

    def test_run_dump_flag(self):
        """
        Test run with dump flag set.
        """
        patch_dump = unittest.mock.patch.object(pyld.PythonLoader, 'dump', return_value=None)
        patch_dump.start()
        self._mock_options.get_dump_flag = unittest.mock.MagicMock(return_value=True)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

        self.assertTrue(python_loader.dump.called)

    def test_run_import_error(self):
        """
        Test run failure when module does not exist
        """
        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

    def test_run_import_main(self):
        """
        Test run loads module and calls 'Main()'. We use this module as the test module.
        """
        self._mock_options.get_module = unittest.mock.MagicMock(return_value='test_pyld')
        self._mock_options.get_module_dir = unittest.mock.MagicMock(return_value=os.curdir)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(AttributeError) as context:
            python_loader.run()

        self.assertIsInstance(context.exception.args, tuple)
        self.assertIn("has no attribute 'Main'", context.exception.args[0])

    def test_run_library_path(self):
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

    def test_run_pyldverbose_flag(self):
        """
        Test run with '-pyldverbose' flag on.
        """
        self._mock_options.get_verbose_flag = unittest.mock.MagicMock(return_value=True)

        python_loader = pyld.PythonLoader(self._mock_options)

        with self.assertRaises(FileNotFoundError):
            python_loader.run()

        value = pyld.sys.stdout.getvalue()
        self.assertIsInstance(value, str)
        self.assertIn('sys.argv =', value)

    def test_get_options(self):
        """
        Test options is set correctly.
        """
        python_loader = pyld.PythonLoader(self._mock_options)

        value = python_loader.get_options()
        self.assertIsInstance(value, unittest.mock.MagicMock)
        self.assertEqual(value, self._mock_options)

    def test_get_sys_argv(self):
        """
        Test getting Python system arguments (faked by pyld).
        """
        python_loader = pyld.PythonLoader(self._mock_options)

        value = python_loader.get_sys_argv()
        self.assertIsInstance(value, list)
        self.assertListEqual(value, [os.path.join('directory', 'arg0'), 'args1', 'args2'])


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        print('\n' + __file__ + ':unittest.main(verbosity=2, buffer=True):')
        unittest.main(verbosity=2, buffer=True)
