#!/usr/bin/env python3
"""
Load Python main program as module (must have Main class).
"""

import argparse
import glob
import importlib.machinery
import importlib.util
import os
import signal
import sys

if sys.version_info < (3, 5) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.5, < 4.0).")
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]


class Options:
    """
    This class handles Python loader commandline options.

    self._args.module = Module name containing 'Main(args)' class
    self._dump_flag = Dump objects flag
    self._library_path = Python library path for debug modules
    self._module_args = Arguments for 'Main(args)' class
    self._module_dir = Directory containing Python modules
    self._verbose_flag = Verbose flag
    """

    def dump(self):
        """
        Dump object recursively.
        """
        print('    "_options": {')
        print('        "_args": {')
        print('            "args":', str(self._args.args), ',')
        print('            "libpath":', str(self._args.libpath) + ',')
        print('            "module":' + str(self._args.module) + ',')
        print('            "verbosity":', self._args.verbosity)
        print("        },")
        print('        "_dump_flag":', str(self._dump_flag) + ',')
        print('        "_library_path":', str(self._library_path) + ',')
        print('        "_module_name":', str(self._module_name) + ',')
        print('        "_module_args":', str(self._module_args) + ',')
        print('        "_module_dir": "', self._module_dir, '",')
        print('        "_verbose_flag":', self._verbose_flag)
        print("    },")

    def __init__(self, args):
        """
        args = Python loader commandline arguments
        """
        self._module_dir = os.path.dirname(args[0])
        self._parse_args(args[1:])

    def get_dump_flag(self):
        """
        Return dump objects flag.
        """
        return self._dump_flag

    def get_library_path(self):
        """
        Return Python library path for debug modules.
        """
        return self._library_path

    def get_module(self):
        """
        Return module name containing 'Main(args)' class
        """
        return self._args.module[0]

    def get_module_name(self):
        """
        Return module name.
        """
        return self._module_name

    def get_module_args(self):
        """
        Return main module arguments.
        """
        return self._module_args

    def get_module_dir(self):
        """
        Return main module directory.
        """
        return self._module_dir

    def get_verbose_flag(self):
        """
        Return verbose flag.
        """
        return self._verbose_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Load Python main program as module '
            '(must have Main class).'
        )

        parser.add_argument(
            '-pyldv',
            '-pyldvv',
            '-pyldvvv',
            nargs=0,
            action=ArgparseVerboseAction,
            dest='verbosity',
            default=0,
            help='Select verbosity level 1, 2 or 3.'
        )
        parser.add_argument(
            '-pyldverbose',
            action='store_const',
            const=1,
            dest='verbosity',
            default=0,
            help='Select verbosity level 1.'
        )
        parser.add_argument(
            '-pyldname',
            nargs=1,
            dest='name',
            default=None,
            help='Select module name.'
        )
        parser.add_argument(
            '-pyldpath',
            nargs=1,
            dest='libpath',
            help='Add directories to the python load path.'
        )
        parser.add_argument(
            'module',
            nargs=1,
            help='Module to run.'
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help='Module argument.'
        )

        py_args = []
        mod_args = []
        while args:
            if args[0] in {
                    '-pyldv',
                    '-pyldvv',
                    '-pyldvvv',
                    '-pyldverbose',
                    '-pyldname',
                    '-pyldpath'
            }:
                py_args.append(args[0])
                if args[0] in ('-pyldname', '-pyldpath') and len(args) >= 2:
                    args = args[1:]
                    py_args.append(args[0])
            elif (
                    args[0].startswith('-pyldname=') or
                    args[0].startswith('-pyldpath=')
            ):
                py_args.extend(args[0].split('=', 1))
            else:
                mod_args.append(args[0])
            args = args[1:]
        py_args.extend(mod_args[:1])

        self._args = parser.parse_args(py_args)

        self._verbose_flag = self._args.verbosity >= 1
        self._dump_flag = self._args.verbosity >= 2
        if self._args.name:
            self._module_name = self._args.name[0]
        else:
            self._module_name = self._args.module[0]
        self._module_args = mod_args[1:]
        if self._args.libpath:
            self._library_path = self._args.libpath[0].split(os.path.pathsep)
        else:
            self._library_path = []


# pylint: disable = too-few-public-methods,no-value-for-parameter
class ArgparseVerboseAction(argparse.Action):
    """
    Arg parser verbose action handler class
    """

    def __call__(self, parser, args, values, option_string=None):
        # option_string must be '-pyldv', '-pyldvv' or '-pldyvvv'
        setattr(args, self.dest, len(option_string[5:]))
# pylint: enable = too-few-public-methods,no-value-for-parameter


class PythonLoader:
    """
    This class handles Python loading

    self._options = Options class object
    self._sys_argv = Modified Python system arguments
    """

    def dump(self):
        """
        Dump object recursively.
        """
        print('"pyloader": {')
        self._options.dump()
        print('    "_sysArgv":', self._sys_argv)
        print("}")

    def __init__(self, options):
        """
        options = Options class object
        """
        self._options = options

        name = options.get_module_name()
        self._sys_argv = [
            os.path.join(options.get_module_dir(), name)
        ] + options.get_module_args()

        directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        path = os.environ.get('PATH', '').split(os.pathsep)
        if directory not in path:
            os.environ['PATH'] = os.pathsep.join([directory] + path)

    @staticmethod
    def _load_module(file):
        loader = importlib.machinery.SourceFileLoader('module.name', file)
        main = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(loader.name, loader)
        )
        loader.exec_module(main)
        return main

    def run(self):
        """
        Load main module and run 'Main()' class
        """
        if self._options.get_dump_flag():
            self.dump()
        if self._options.get_library_path():
            sys.path = self._options.get_library_path() + sys.path
            if self._options.get_verbose_flag():
                print("sys.path =", sys.path)

        directory = self._options.get_module_dir()
        if directory not in sys.path:
            sys.path.append(directory)

        module = self._options.get_module()
        if module.endswith('.py'):
            module = module[:-3]

        sys.argv = self._sys_argv
        if self._options.get_verbose_flag():
            print("sys.argv =", sys.argv)
            print()

        main = self._load_module(os.path.join(directory, module)+'.py')
        main.Main()

    def get_options(self):
        """
        Return Options class object.
        """
        return self._options

    def get_sys_argv(self):
        """
        Return list sysArgv.
        """
        return self._sys_argv


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options(sys.argv)
        PythonLoader(options).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
