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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    self._args.noskipFlag = No compile skip flag
    self._dump_flag        = Dump objects flag
    self._modules         = List of module names
    self._verbose_flag     = Verbose flag
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._modules = []
        for file in self._args.files:
            if file.endswith('.py'):
                self._modules.append(PythonModule(file[:-3]))

    def get_dump_flag(self):
        """
        Return dump objects flag.
        """
        return self._dump_flag

    def get_modules(self):
        """
        Return list of PythonModule class objects.
        """
        return self._modules

    def get_noskip_flag(self):
        """
        Return noskip flag.
        """
        return self._args.noskipFlag

    def get_verbose_flag(self):
        """
        Return verbose flag.
        """
        return self._verbose_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check and compile Python 3.x modules to ".pyc" byte code.')

        parser.add_argument('-v', '-vv', '-vvv', nargs=0, action=ArgparseVerboseAction,
                            dest='verbosity', default=0, help='Select verbosity level 1, 2 or 3.')
        parser.add_argument('-verbose', action='store_const', const=1, dest='verbosity',
                            default=0, help='Select verbosity level 1.')
        parser.add_argument('-noskip', dest='noskipFlag', action='store_true',
                            help='Disable skipping of compilation even if ".pyc" exists.')

        parser.add_argument('files', nargs='+', metavar='file.py',
                            help='Python module file.')

        self._args = parser.parse_args(args)

        self._verbose_flag = self._args.verbosity >= 1
        self._dump_flag = self._args.verbosity >= 2


class ArgparseVerboseAction(argparse.Action):
    """
    Arg parser verbose action handler class
    """

    def __call__(self, parser, args, values, option_string=None):
        # option_string must be '-v', '-vv' or '-vvv'
        setattr(args, self.dest, len(option_string[1:]))


class PythonChecker(object):
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
        self._py2to3.set_flags(['--nofix=dict', '--nofix=future', '--nofix=imports',
                               '--nofix=raise', '--nofix=unicode', '--nofix=xrange'])
        self._py2to3.set_wrapper(syslib.Command(file=sys.executable))

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
                            self._py2to3.extend_flags(
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
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" Python module file.')
        if self._python3(file):
            error = True
        return error

    def _python3(self, file):
        error = False
        self._py2to3.set_args([file])
        self._py2to3.run(mode='batch', error2output=True)
        if self._py2to3.is_match_output('^RefactoringTool: Can"t parse '):
            for line in self._py2to3.get_output():
                if line.startswith('RefactoringTool: Can"t parse'):
                    print(file, ': ', line[17:], sep='')
                    error = True
                elif ': Generating grammar tables from ' in line:
                    # Ignore ': Generating grammar tables from /usr/lib/.../PatternGrammar.txt'
                    pass
                elif line[:17] != 'RefactoringTool: ':
                    print(file, ': ', line, sep='')
                    error = True
        elif not self._py2to3.is_match_output('No files need to be modified.'):
            for line in self._py2to3.get_output():
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


class PythonCompiler(object):
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
        if self._options.get_dump_flag():
            syslib.Dump().list('pyc', self)

        self._umask = os.umask(int('022', 8))
        errors = 0

        verboseFlag = self._options.get_verbose_flag()
        for module in self._options.get_modules():
            if verboseFlag:
                print('\nChecking', module.get_source())
            if self._options.get_noskip_flag() or not module.check_target():
                source = module.get_source()
                print('\nCompiling "' + source + '"...')
                if self._checker.run(source):
                    errors += 1
                else:
                    if self._build_target(module):
                        errors += 1

        print()
        if errors > 0:
            raise SystemExit('Total errors encountered: ' + str(errors) + '.')

    def _build_target(self, module):
        try:
            py_compile.compile(module.get_source())
        except py_compile.PyCompileError as exception:
            return 1
        module.update_target()
        return 0


class PythonModule(object):
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

    def check_target(self):
        """
        Return True if '.pyc' exists.
        """
        if os.path.isfile(self._target):
            if syslib.FileStat(self._target).get_time() == syslib.FileStat(self._source).get_time():
                return True
        return False

    def update_target(self):
        """
        Set target file modification time to source file.
        """
        timeNew = syslib.FileStat(self._source).get_time()
        os.utime(self._target, (timeNew, timeNew))

    def get_source(self):
        """
        Return source file location.
        """
        return self._source

    def get_target(self):
        """
        Return target file location.
        """
        return self._target


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
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

    def _windows_argv(self):
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
