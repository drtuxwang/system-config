#!/usr/bin/env python3
"""
Load Python main program as module (must have Main class).
"""

import argparse
import glob
import importlib.machinery
import os
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]


class Options:
    """
    This class handles Python loader commandline options.

    self._args.module = Module name containing 'Main(args)' class
    self._dumpFlag    = Dump objects flag
    self._libraryPath = Python library path for debug modules
    self._moduleArgs  = Arguments for 'Main(args)' class
    self._moduleDir   = Directory containing Python modules
    self._verboseFlag = Verbose flag
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
        print('        },')
        print('        "_dumpFlag":', str(self._dumpFlag) + ',')
        print('        "_libraryPath":', str(self._libraryPath) + ',')
        print('        "_moduleArgs":', str(self._moduleArgs) + ',')
        print('        "_moduleDir": "', self._moduleDir, '",')
        print('        "_verboseFlag":', self._verboseFlag)
        print('    },')

    def __init__(self, args):
        """
        args = Python loader commandline arguments
        """
        self._parseArgs(args[1:])

        self._moduleDir = os.path.dirname(args[0])

    def getDumpFlag(self):
        """
        Return dump objects flag.
        """
        return self._dumpFlag

    def getLibraryPath(self):
        """
        Return Python library path for debug modules.
        """
        return self._libraryPath

    def getModule(self):
        """
        Return module name containing 'Main(args)' class
        """
        return self._args.module[0]

    def getModuleArgs(self):
        """
        Return main module arguments.
        """
        return self._moduleArgs

    def getModuleDir(self):
        """
        Return main module directory.
        """
        return self._moduleDir

    def getVerboseFlag(self):
        """
        Return verbose flag.
        """
        return self._verboseFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Load Python main program as module (must have Main class).')

        parser.add_argument('-pyldv', '-pyldvv', '-pyldvvv', nargs=0, action=ArgparseActionVerbose,
                            dest='verbosity', default=0, help='Select verbosity level 1, 2 or 3.')
        parser.add_argument('-pyldverbose', action='store_const', const=1, dest='verbosity',
                            default=0, help='Select verbosity level 1.')
        parser.add_argument('-pyldpath', nargs=1, dest='libpath',
                            help='Add directories to the python load path.')

        parser.add_argument('module', nargs=1, help='Module to run.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Module argument.')

        pyArgs = []
        modArgs = []
        while len(args):
            if args[0] in ('-pyldv', '-pyldvv', '-pyldvvv', '-pyldverbose', '-pyldpath'):
                pyArgs.append(args[0])
                if args[0] == '-pyldpath' and len(args) >= 2:
                    args = args[1:]
                    pyArgs.append(args[0])
            elif args[0].startswith('-pyldpath='):
                pyArgs.append(args[0])
            else:
                modArgs.append(args[0])
            args = args[1:]
        pyArgs.extend(modArgs[:1])

        self._args = parser.parse_args(pyArgs)

        self._verboseFlag = self._args.verbosity >= 1
        self._dumpFlag = self._args.verbosity >= 2
        self._moduleArgs = modArgs[1:]
        if self._args.libpath:
            self._libraryPath = self._args.libpath[0].split(os.path.pathsep)
        else:
            self._libraryPath = []


class ArgparseActionVerbose(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        # option_string must be '-pyldv', '-pyldvv' or '-pldyvvv'
        setattr(args, self.dest, len(option_string[5:]))


class PythonLoader:
    """
    This class handles Python loading

    self._options = Options class object
    self._sysArgv = Modified Python system arguments
    """

    def dump(self):
        """
        Dump object recursively.
        """
        print('"pyloader": {')
        self._options.dump()
        print('    "_sysArgv":', self._sysArgv)
        print('}')

    def __init__(self, options):
        """
        options = Options class object
        """
        self._options = options
        self._sysArgv = [os.path.join(options.getModuleDir(),
                         options.getModule() + '.py')] + options.getModuleArgs()

    def run(self):
        """
        Load main module and run 'Main()' class
        """
        if self._options.getDumpFlag():
            self.dump()
        if self._options.getLibraryPath():
            sys.path = self._options.getLibraryPath() + sys.path
            if self._options.getVerboseFlag():
                print('sys.path =', sys.path)

        directory = self._options.getModuleDir()
        if directory not in sys.path:
            sys.path.append(directory)

        module = self._options.getModule()
        if module.endswith('.py'):
            module = module[:-3]

        sys.argv = self._sysArgv
        if self._options.getVerboseFlag():
            print('sys.argv =', sys.argv)
            print()

        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        main = importlib.machinery.SourceFileLoader(
            "module.name", os.path.join(directory, module) + '.py').load_module()
        main.Main()

    def getOptions(self):
        """
        Return Options class object.
        """
        return self._options

    def getSysArgv(self):
        """
        Return list sysArgv.
        """
        return self._sysArgv


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            PythonLoader(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
