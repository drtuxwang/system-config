#!/usr/bin/env python3
"""
Run Python unittests in module files.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):
    """
    This class handles Python loader commandline options.

    self._dumpFlag    = Dump objects flag
    self._files       = List of Python test module files
    self._verboseFlag = Verbose flag
    """

    def __init__(self, args):
        """
        args = Python test commandline arguments
        """
        self._parseArgs(args[1:])

    def getDumpFlag(self):
        """
        Return dump objects flag.
        """
        return self._dumpFlag

    def getFiles(self):
        """
        Return list of test modules
        """
        return self._files

    def getVerboseFlag(self):
        """
        Return verbose flag.
        """
        return self._verboseFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Run Python unittests in module files.')

        parser.add_argument('-v', '-vv', '-vvv', nargs=0, action=ArgparseActionVerbose,
                            dest='verbosity', default=0, help='Select verbosity level 1, 2 or 3.')
        parser.add_argument('-verbose', action='store_const', const=1, dest='verbosity',
                            default=0, help='Select verbosity level 1.')
        parser.add_argument('files', nargs='+', metavar='test_file.py',
                            help='Python unittest module file.')

        self._args = parser.parse_args(args)

        self._verboseFlag = self._args.verbosity >= 1
        self._dumpFlag = self._args.verbosity >= 2

        self._files = []
        for file in self._args.files:
            if file.startswith('test_') and file.endswith('.py'):
                self._files.append(file)


class ArgparseActionVerbose(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        # option_string must be '-v', '-vv' or '-vvv'
        setattr(args, self.dest, len(option_string[1:]))


class ModuleTest(syslib.Dump):
    """
    This class deals with Python module unit testing

    self._file    = Python module file
    self._options = Options class object
    self._python3 = Python3 Command class object
    """

    def __init__(self, options, file):
        """
        file    = Python module file
        option  = Option class object
        """
        self._options = options
        self._file = file
        self._python3 = syslib.Command(file=sys.executable)
        self._python3.setFlags(['-m', 'unittest', '-v', '-b'])

    def run(self):
        """
        Run unittest test discovery on Python module.
        """
        directory = os.path.dirname(self._file)
        self._python3.setArgs([os.path.basename(self._file)])
        self._python3.run(directory=directory, mode='batch', error2output=True)

        if self._python3.getExitcode():
            for line in self._python3.getOutput():
                print(line, file=sys.stderr)
        elif self._options.getVerboseFlag():
            for line in self._python3.getOutput():
                print(line)
        else:
            try:
                print(self._python3.getOutput()[-3])
            except (IndexError, ValueError):
                for line in self._python3.getOutput():
                    print(line)

    def getTests(self):
        """
        Return the number of tests ran.
        """
        try:
            return int(self._python3.getOutput()[-3].split()[1])
        except (IndexError, ValueError):
            return 0

    def getFailures(self):
        """
        Return the number of test failures.
        """
        for line in reversed(self._python3.getOutput()):
            if line.startswith('FAILED (') and 'failures=' in line:
                try:
                    return int(line.split('failures=')[1].split(',')[0].split(')')[0])
                except (IndexError, ValueError):
                    pass
        return 0

    def getErrors(self):
        """
        Return the number of test code errors.
        """
        for line in reversed(self._python3.getOutput()):
            if line.startswith('FAILED (') and 'errors=' in line:
                try:
                    return int(line.split('errors=')[1].split(')')[0])
                except (IndexError, ValueError):
                    pass
        return 0

    def getExitError(self):
        """
        Return exit code errors.
        """
        return min(self._python3.getExitcode(), 1)


class PythonTest(syslib.Dump):
    """
    This class performs Python unit testing

    self._options = Options class object
    """

    def __init__(self, options):
        """
        options = Options class object
        """
        self._options = options

    def run(self):
        """
        Run all test suites
        """
        if self._options.getDumpFlag():
            self.dump('pytest.')

        startTime = time.time()
        tests = 0
        failures = 0
        errors = 0
        exitErrors = 0
        for file in self._options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" Python module file.')
            print('\nRunning "' + os.path.abspath(file) + '"...')

            moduleTest = ModuleTest(self._options, file)
            moduleTest.run()
            tests += moduleTest.getTests()
            failures += moduleTest.getFailures()
            errors += moduleTest.getErrors()
            exitErrors += moduleTest.getExitError()

        print('\nUnit Test runs      =', tests)
        print('Unit Test failures  =', failures)
        print('Testing code errors =', errors)
        print('Exit code errors    =', exitErrors)
        print('Total elapsed time  = {0:5.3f}s'.format(time.time() - startTime))
        if failures + errors + exitErrors:
            raise SystemExit(1)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            PythonTest(options).run()
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
