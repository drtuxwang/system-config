#!/usr/bin/env python3
"""
Check and compile Python 3.x modules to '.pyc' byte code.
"""

import argparse
import glob
import os
import py_compile
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:
    """
    self._args.noskipFlag = No compile skip flag
    self._dumpFlag        = Dump objects flag
    self._modules         = List of module names
    self._verboseFlag     = Verbose flag
    """

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._modules = []
        for file in self._args.files:
            if file.endswith('.py'):
                self._modules.append(PythonModule(file[:-3]))

    def getDumpFlag(self):
        """
        Return dump objects flag.
        """
        return self._dumpFlag

    def getModules(self):
        """
        Return list of PythonModule class objects.
        """
        return self._modules

    def getNoskipFlag(self):
        """
        Return noskip flag.
        """
        return self._args.noskipFlag

    def getVerboseFlag(self):
        """
        Return verbose flag.
        """
        return self._verboseFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Check and compile Python 3.x modules to ".pyc" byte code.')

        parser.add_argument('-v', '-vv', '-vvv', nargs=0, action=ArgparseActionVerbose,
                            dest='verbosity', default=0, help='Select verbosity level 1, 2 or 3.')
        parser.add_argument('-verbose', action='store_const', const=1, dest='verbosity',
                            default=0, help='Select verbosity level 1.')
        parser.add_argument('-noskip', dest='noskipFlag', action='store_true',
                            help='Disable skipping of compilation even if ".pyc" exists.')

        parser.add_argument('files', nargs='+', metavar='file.py',
                            help='Python module file.')

        self._args = parser.parse_args(args)

        self._verboseFlag = self._args.verbosity >= 1
        self._dumpFlag = self._args.verbosity >= 2


class ArgparseActionVerbose(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        # option_string must be '-v', '-vv' or '-vvv'
        setattr(args, self.dest, len(option_string[1:]))


class PythonChecker:
    """
    This class checks Python source code for 3.x compatibility and common mistakes.
    """

    def __init__(self):
        if os.name == 'nt':
            self._py2to3 = syslib.Command(
                file=os.path.join(os.path.dirname(sys.executable), 'Tools', 'Scripts', '2to3.py'))
        else:
            file = os.path.join(os.path.dirname(sys.executable), '2to3')
            if os.path.isfile(file + '.py'):
                file += '.py'
            self._py2to3 = syslib.Command(file=file)
        self._py2to3.setFlags(['--nofix=dict', '--nofix=future', '--nofix=imports',
                               '--nofix=raise', '--nofix=unicode', '--nofix=xrange'])
        self._py2to3.setWrapper(syslib.Command(file=sys.executable))

    def _check(self, file):
        error = False
        try:
            with open(file, errors='replace') as ifile:
                n = 0
                for line in ifile:
                    line = line.rstrip('\r\n')
                    n += 1
                    if n == 1:
                        if not line.startswith('#!/'):
                            return 0
                        elif 'python' not in line:  # Not Python program
                            return 0
                        elif 'python3' in line:
                            self._py2to3.extendFlags(
                                ['--nofix=input', '--nofix=print', '--print-function'])
                        if not line.startswith('#!/usr/bin/env python'):
                            print(file, ': ? line 1 should be "#!/usr/bin/env python".', sep='')
                            error = True
                    if len(line) > 100:
                        print(file + ': line', n, 'contains more than 100 characters. '
                              'Please use continuation line.')
                        error = True
                    if 'except:' in line and '"except:' not in line:
                        print(file, ': ? line ', n,
                              ' contains exception with no name "except:".', sep='')
                        error = True
                    if line.endswith(' '):
                        print(file, ': ? line ', n, ' contains space at end of line.', sep='')
                        error = True
                    if '\t' in line:
                        print(file, ': ? line ', n, ' contains tab instead of spaces.', sep='')
                        error = True
        except (IOError):
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" Python module file.')
        if self._python3(file):
            error = True
        return error

    def _python3(self, file):
        error = False
        self._py2to3.setArgs([file])
        self._py2to3.run(mode='batch', error2output=True)
        if self._py2to3.isMatchOutput('^RefactoringTool: Can"t parse '):
            for line in self._py2to3.getOutput():
                if line.startswith('RefactoringTool: Can"t parse'):
                    print(file, ': ', line[17:], sep='')
                    error = True
                elif ': Generating grammar tables from ' in line:
                    # Ignore ': Generating grammar tables from /usr/lib/.../PatternGrammar.txt'
                    pass
                elif line[:17] != 'RefactoringTool: ':
                    print(file, ': ', line, sep='')
                    error = True
        elif not self._py2to3.isMatchOutput('No files need to be modified.'):
            for line in self._py2to3.getOutput():
                if ': Generating grammar tables from ' in line:
                    # Ignore ': Generating grammar tables from /usr/lib/.../PatternGrammar.txt'
                    pass
                elif line[:17] != 'RefactoringTool: ':
                    if line[:3] not in ('---', '+++'):
                        print(file, ': ', line, sep='')
                        error = True
        return error

    def run(self, file):
        if not os.path.isdir(file):
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" Python module file.')
            if self._check(file):
                return 1
        return 0


class PythonCompiler:
    """
    This class check & compiles Python source code into '.pyc' (works like make).
    """

    def __init__(self, options):
        """
        options = Options class object
        """
        self._options = options
        self._checker = PythonChecker()
        if 'PYTHONDONTWRITEBYTECODE' in os.environ:
            del os.environ['PYTHONDONTWRITEBYTECODE']

    def run(self):
        """
        Compiles Python with verbose error messages
        """
        if self._options.getDumpFlag():
            syslib.Dump().list('pyc', self)

        self._umask = os.umask(int('022', 8))
        errors = 0

        verboseFlag = self._options.getVerboseFlag()
        for module in self._options.getModules():
            if verboseFlag:
                print('\nChecking', module.getSource())
            if self._options.getNoskipFlag() or not module.checkTarget():
                source = module.getSource()
                print('\nCompiling "' + source + '"...')
                if self._checker.run(source):
                    errors += 1
                else:
                    if self._buildTarget(module):
                        errors += 1

        print()
        if errors > 0:
            raise SystemExit('Total errors encountered: ' + str(errors) + '.')

    def _buildTarget(self, module):
        try:
            py_compile.compile(module.getSource())
        except py_compile.PyCompileError as exception:
            return 1
        module.updateTarget()
        return 0


class PythonModule:
    """
    This class deals with Python module files.
    """

    def __init__(self, module):
        """
        module = Module name
        """
        extension = '.cpython-' + str(sys.version_info[0]) + str(sys.version_info[1]) + '.pyc'
        self._source = module + '.py'
        self._target = os.path.join(os.path.dirname(module), '__pycache__',
                                    os.path.basename(module) + extension)

    def checkTarget(self):
        """
        Return True if '.pyc' exists.
        """
        if os.path.isfile(self._target):
            if syslib.FileStat(self._target).getTime() == syslib.FileStat(self._source).getTime():
                return True
        return False

    def updateTarget(self):
        """
        Set target file modification time to source file.
        """
        timeNew = syslib.FileStat(self._source).getTime()
        os.utime(self._target, (timeNew, timeNew))

    def getSource(self):
        """
        Return source file location.
        """
        return self._source

    def getTarget(self):
        """
        Return target file location.
        """
        return self._target


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            sys.exit(PythonCompiler(options).run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
