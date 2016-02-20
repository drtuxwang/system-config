#!/usr/bin/env python3
"""
Python command line handling module

Copyright GPL v2: 2006-2016 By Dr Colin Kong

Version 2.0.2 (2016-02-20)
"""

import distutils
import functools
import glob
import os
import re
import subprocess
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Command(object):
    """
    This class stores a command (uses supplied executable)
    """

    def __init__(self, program, **flags):
        """
        program   = Command program name (ie 'evince', 'bin/acroread')
        args      = Optional command arguments list
        pathextra = Optional extra PATH to prefix in search
        platform  = Optional platform (ie 'windows-x86_64' for WINE)
        errors    = Optional error handling ('stop' or 'ignore')
        """
        self._args = [self._locate(program, **flags)]
        try:
            self._args = self._args.extend(flags['args'])
        except KeyError:
            pass

    @classmethod
    def _locate(cls, program, **flags):
        try:
            platform = flags['platform']
        except KeyError:
            platform = _System.get_platform()
        extensions = cls._get_extensions(platform)

        directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.basename(directory) == 'bin':
            directory = os.path.dirname(directory)
            file = cls._search_ports(directory, platform, program, extensions)
            if file:
                return file

        try:
            pathextra = flags['pathextra']
        except KeyError:
            pathextra = []
        file = cls._search_path(pathextra, program, extensions)
        if file:
            return file

        try:
            if flags['errors'] == 'stop':
                raise SystemExit(sys.argv[0] + ': Cannot find required "' + program + '" software.')
            elif flags['errors'] == 'ignore':
                return ''
        except KeyError:
            pass
        raise CommandNotFoundError(
            sys.argv[0] + ': Cannot find required "' + program + '" software.')

    @staticmethod
    def _get_extensions(platform):
        extensions = ['']
        if platform.startswith('windows-'):
            try:
                extensions.extend(os.environ['PATHEXT'].lower().split(os.pathsep))
            except KeyError:
                pass
        return extensions

    @staticmethod
    def _check_glibc(files):
        has_glibc = re.compile(r'-glibc_\d+[.]\d+([.]\d+)?')
        nfiles = []
        for file in files:
            if has_glibc.search(file):
                version = file.split('-glibc_')[1].split('-')[0].split('/')[0]
                if (distutils.version.LooseVersion(_System.get_glibc()) >=
                        distutils.version.LooseVersion(version)):
                    nfiles.append(file)
            else:
                nfiles.append(file)
        return nfiles

    @classmethod
    def _search_ports(cls, directory, platform, program, extensions):
        for port_glob in _System.get_port_globs(platform):
            for extension in extensions:
                files = glob.glob(os.path.join(directory, '*', port_glob, program + extension))
                if platform.startswith('linux'):
                    files = cls._check_glibc(files)
                if files:
                    return files

        # Search directories with 4 or more characters as fall back for local port
        if not files:
            for extension in extensions:
                files = glob.glob(os.path.join(directory, '????*', program + extension))
                if files:
                    break
        if files:
            return _System.newest(files)

        return None

    @staticmethod
    def _search_path(pathextra, program, extensions):
        # Shake PATH to make it unique
        paths = []
        for path in list(pathextra) + os.environ['PATH'].split(os.pathsep):
            if path:
                if path not in paths:
                    paths.append(path)

        # Prevent recursion
        program = os.path.basename(program)
        if os.path.basename(sys.argv[0]) in (program, program + '.py'):
            mydir = os.path.dirname(sys.argv[0])
            if mydir in paths:
                paths = paths[paths.index(mydir) + 1:]

        if sys.argv[0].endswith('.py'):
            mynames = (sys.argv[0][:-3], sys.argv[0])
        else:
            mynames = (sys.argv[0], sys.argv[0] + '.py')
        for directory in paths:
            if os.path.isdir(directory):
                for extension in extensions:
                    file = os.path.join(directory, program) + extension
                    if os.path.isfile(file):
                        if file not in mynames:
                            return file

        return None

    @staticmethod
    def args2cmd(args):
        """
        Join list of arguments into a command string.

        args = List of arguments
        """
        return subprocess.list2cmdline(args)

    @staticmethod
    def _cmd2chars(cmd):
        chars = []
        backslashs = ''
        for char in cmd:
            if char == '\\':
                backslashs += char
            elif char == '"' and backslashs:
                nbackslashs = len(backslashs)
                chars.extend(['\\'] * (nbackslashs//2))
                backslashs = ''
                if nbackslashs % 2:
                    chars.append(1)
                else:
                    chars.append('"')
            else:
                if backslashs:
                    chars.extend(list(backslashs))
                    backslashs = ''
                chars.append(char)
        return chars

    @staticmethod
    def _chars2args(chars):
        args = []
        arg = []
        quoted = False
        chars.append(' ')
        for char in chars:
            if char == '"':
                quoted = not quoted
            elif char == 1:
                arg.append('"')
            elif char in (' ', '\t'):
                if quoted:
                    arg.append(char)
                elif arg:
                    args.append(''.join(arg))
                    arg = []
            else:
                arg.append(char)
        return args

    @classmethod
    def cmd2args(cls, cmd):
        """
        Split a command string into a list of arguments.
        """
        chars = cls._cmd2chars(cmd)
        args = cls._chars2args(chars)
        return args

    def get_cmdline(self):
        """
        Return the command line as a list.
        """
        if os.name == 'nt':
            try:
                with open(self._args[0]) as ifile:
                    if ifile.readline().startswith('#!/usr/bin/env python'):
                        return [sys.executable] + self._args
            except OSError:
                pass
        return self._args

    def get_file(self):
        """
        Return file location.
        """
        return self._args[0]

    def get_args(self):
        """
        Return list of arguments.
        """
        return self._args[1:]

    def append_arg(self, arg):
        """
        Append to command line arguments

        arg = Argument
        """
        self._args.append(arg)

    def extend_args(self, args):
        """
        Extend command line arguments

        args = List of arguments
        """
        self._args.extend(args)

    def set_args(self, args):
        """
        Set command line arguments

        args = List of arguments
        """
        self._args[1:] = args

    def is_found(self):
        """
        Return True if file is defined.
        """
        return self._args[0] != ''


class CommandFile(Command):
    """
    This class stores a command (uses supplied executable)
    """

    def __init__(self, file, **flags):
        """
        file = Full PATH to executable
        args = Optional command arguments list
        """
        super().__init__(file, **flags)

    @staticmethod
    def _locate(file, **flags):
        return file


class _System(object):

    @staticmethod
    def _get_linux_platform(machine):
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine.endswith('86'):
            arch = 'x86'
        elif machine == 'sparc64':
            arch = 'sparc64'
        elif machine == 'ppc64':
            arch = 'power64'
        return 'linux-' + arch

    @staticmethod
    def _get_macos_platform(machine):
        # "/usr/sbin/sysct -a" => "hw.cpu64bit_capable: 1"
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine == 'i386':
            arch = 'x86'
        return 'macos-' + arch

    @staticmethod
    def _get_windows_platform():
        arch = 'unknown'
        if 'PROCESSOR_ARCHITECTURE' in os.environ:
            if os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64':
                arch = 'x86_64'
            elif ('PROCESSOR_ARCHITEW6432' in os.environ and
                  os.environ['PROCESSOR_ARCHITEW6432'] == 'AMD64'):
                arch = 'x86_64'
            elif os.environ['PROCESSOR_ARCHITECTURE'] == 'x86':
                arch = 'x86'
        return 'windows-' + arch

    @staticmethod
    def _get_windows_cygwin_platform(kernel, machine):
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine.endswith('86'):
            if 'WOW64' in kernel:
                arch = 'x86_64'
            else:
                arch = 'x86'
        return 'Windows_' + arch

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_platform(cls):
        """
        Return platform (ie linux-x86, linux-x86_64, macos-x86_64, windows-x86_64).
        """
        platform = ('unknown', 'unknown')
        if os.name == 'nt':
            platform = cls._get_windows_platform()
        else:
            kernel, *_, machine = os.uname()
            if kernel == 'Linux':
                platform = cls._get_linux_platform(machine)
            elif kernel == 'Darwin':
                platform = cls._get_macos_platform(machine)
            elif kernel.startswith('cygwin'):
                platform = cls._get_windows_cygwin_platform(kernel, machine)
        return platform

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_port_globs(platform):
        """
        Return tuple of portname globs (ie 'linux64_*-x86*', 'windows64_*-x86*')
        """
        mapping = {'linux-x86_64': ('linux64_*-x86*', 'linux_*-x86*'),
                   'linux-x86': ('linux_*-x86*'),
                   'linux-sparc64': ('linux64_*-sparc64*', 'linux_*-sparc*'),
                   'linux-power64': ('linux64_*-power64*', 'linux_*-power*'),
                   'macos-x86_64': ('macos64_*-x86*', 'macos_*-x86*'),
                   'macos-x86': ('macos_*-x86*'),
                   'windows-x86_64': ('windows64_*-x86*', 'windows_*-x86*'),
                   'windows-x86': ('windows_*-x86*')}

        try:
            return mapping[platform]
        except KeyError:
            return ()

    @staticmethod
    def _get_file_time(file):
        try:
            return os.stat(file)[8]
        except (OSError, TypeError):
            return 0

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_glibc(cls):
        """
        Return glibc version string
        (based on glibc version used to compile 'ldd' or return '0.0' for non Linux)
        """
        if cls.get_platform().startswith('linux'):
            ldd = syslib.Command('ldd', args=['--version'], check=False)
            if not ldd.is_found():
                raise CommandLddNotFoundError(
                    sys.argv[0] + ': Cannot find required "ldd" software.')
            ldd.run(filter='^ldd ', mode='batch')
            return ldd.get_output()[0].split()[-1]
        return '0.0'

    @classmethod
    def newest(cls, files):
        """
        Return newest file or directory.

        files = List of files
        """
        nfile = ''
        nfile_time = -1

        for file in files:
            if os.path.isfile(file) or os.path.isdir(file):
                file_time = cls._get_file_time(file)
                if file_time > nfile_time:
                    nfile = file
                    nfile_time = file_time

        return nfile


class CommandError(Exception):
    """
    Command module error.
    """


class CommandNotFoundError(CommandError):
    """
    Command not found error.
    """


class CommandLddNotFoundError(CommandError):
    """
    Command 'ldd' not found error.
    """

if __name__ == '__main__':
    help(__name__)
