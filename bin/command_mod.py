#!/usr/bin/env python3
"""
Python sub task handling module

Copyright GPL v2: 2006-2019 By Dr Colin Kong
"""

import distutils.version
import functools
import glob
import os
import platform
import re
import subprocess
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

RELEASE = '2.3.0'
VERSION = 20190908


class Command:
    """
    This class stores a command (uses supplied executable)
    """

    def __init__(self, program, **kwargs):
        """
        program = Command program name (ie 'evince', 'bin/acroread')
        args = Optional command arguments list
        directory = Optional directory for searching local software
        pathextra = Optional extra PATH to prefix in search
        platform = Optional platform (ie 'windows-x86_64' for WINE)
        errors = Optional error handling ('stop' or 'ignore')
        """
        info = self._parse_keys(
            ('args', 'directory', 'errors', 'pathextra', 'platform'),
            **kwargs
        )
        self._args = [self._locate(program, info)]
        try:
            self._args.extend(kwargs['args'])
        except KeyError:
            pass

    @staticmethod
    def _parse_keys(keys, **kwargs):
        if set(kwargs.keys()) - set(keys):
            raise CommandKeywordError(
                'Unsupported keyword "' +
                list(set(kwargs.keys()) - set(keys))[0] + '".'
            )
        info = {}
        for key in keys:
            try:
                info[key] = kwargs[key]
            except KeyError:
                if key == 'pathextra':
                    info[key] = []
                elif key == 'platform':
                    info[key] = ''
                else:
                    info[key] = None
        return info

    @classmethod
    def _locate(cls, program, info):
        _platform = info['platform']
        if not _platform:
            _platform = _System.get_platform()
        extensions = cls._get_extensions(_platform)

        directory = info['directory']
        if not directory:
            directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.basename(directory) == 'bin':
            directory = os.path.dirname(directory)
            file = cls._search_ports(directory, _platform, program, extensions)
            if file:
                return file

        file = cls._search_path(info['pathextra'], program, extensions)
        if file:
            return file

        if info['errors'] == 'stop':
            raise SystemExit(
                sys.argv[0] + ': Cannot find required "' +
                program + '" software.'
            )
        if info['errors'] == 'ignore':
            return ''
        raise CommandNotFoundError(
            'Cannot find required "' + program + '" software.')

    @staticmethod
    def _get_extensions(_platform):
        extensions = ['']
        if _platform.startswith('windows-'):
            try:
                extensions.extend(
                    os.environ['PATHEXT'].lower().split(os.pathsep))
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
    def _search_ports(cls, directory, _platform, program, extensions):
        files = []
        for port_glob in _System.get_port_globs(_platform):
            for extension in extensions:
                files = glob.glob(os.path.join(
                    directory,
                    '*',
                    port_glob,
                    program + extension
                ))
                if _platform.startswith('linux'):
                    files = cls._check_glibc(files)
                if files:
                    return _System.newest(files)

        # Search directories with 4 or more char as fall back for local port
        if not files:
            for extension in extensions:
                files = glob.glob(
                    os.path.join(directory, '????*', program + extension))
                if files:
                    break
        if files:
            return _System.newest(files)

        return None

    @staticmethod
    def _search_path(pathextra, program, extensions):
        program = os.path.basename(program)

        # Shake PATH to make it unique
        paths = []
        for path in list(pathextra) + os.environ['PATH'].split(os.pathsep):
            if path:
                if path not in paths:
                    paths.append(path)

        # Prevent recursion
        if (not pathextra and
                os.path.basename(sys.argv[0]) in (program, program + '.py')):
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

        subprocess.list2cmdline() does not handle "&" properly)
        """
        nargs = []
        for arg in args:
            if '"' in arg or ' ' in arg or '&' in arg:
                nargs.append(
                    '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"'
                )
            else:
                nargs.append(arg)
        return ' '.join(nargs)

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
    This class stores a command (uses supplied executable location)
    """

    @staticmethod
    def _locate(program, info):
        if os.path.isfile(program):
            return program

        if info['errors'] == 'stop':
            raise SystemExit(
                sys.argv[0] + ': Cannot find required "' +
                program + '" software.'
            )
        if info['errors'] == 'ignore':
            return ''
        raise CommandNotFoundError(
            'Cannot find required "' + program + '" software.')


class Platform:
    """
    This class provides some platform information
    """

    @staticmethod
    def _get_arch_linux():
        machine = os.uname()[-1]
        arch = 'unknown'
        if machine == 'x86_64':
            if (
                    glob.glob('/lib*/ld-*') and
                    not glob.glob('/lib*/ld-*x86[_-]64*')
            ):
                arch = 'x86'
            else:
                arch = 'x86_64'
        elif machine.endswith('86'):
            arch = 'x86'
        elif machine == 'sparc64':
            arch = 'sparc64'
        elif machine == 'ppc64':
            arch = 'power64'
        return arch

    @staticmethod
    def _get_arch_macos():
        # "/usr/sbin/sysct -a" => "hw.cpu64bit_capable: 1"
        machine = os.uname()[-1]
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine == 'i386':
            arch = 'x86'
        return arch

    @staticmethod
    def _get_arch_windows():
        arch = 'unknown'
        if 'PROCESSOR_ARCHITECTURE' in os.environ:
            if os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64':
                arch = 'x86_64'
            elif ('PROCESSOR_ARCHITEW6432' in os.environ and
                  os.environ['PROCESSOR_ARCHITEW6432'] == 'AMD64'):
                arch = 'x86_64'
            elif os.environ['PROCESSOR_ARCHITECTURE'] == 'x86':
                arch = 'x86'
        return arch

    @staticmethod
    def _get_arch_windows_cygwin():
        osname, *_, machine = os.uname()[-1]
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine.endswith('86'):
            if 'WOW64' in osname:
                arch = 'x86_64'
            else:
                arch = 'x86'
        return arch

    @staticmethod
    def _locate_program(program):
        for directory in os.environ['PATH'].split(os.pathsep):
            file = os.path.join(directory, program)
            if os.path.isfile(file):
                break
        else:
            raise CommandNotFoundError(
                'Cannot find required "' + program + '" software.')
        return file

    @classmethod
    def _run_program(cls, command):
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        try:
            child = subprocess.Popen(
                [program] + command[1:],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + program + '" program.')
        lines = []
        while True:
            try:
                line = child.stdout.readline().decode('utf-8', 'replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            lines.append(line.rstrip('\r\n'))
        return lines

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_glibc(cls):
        """
        Return glibc version string
        (based on glibc version used to compile 'ldd' or
        return '0.0' for non Linux)
        """
        if cls.get_platform().startswith('linux'):
            lines = cls._run_program(['ldd', '--version'])
            try:
                return lines[0].split()[-1]
            except IndexError:
                raise GlibcVersionError('Cannot determine "glibc" version.')
        return '0.0'

    @staticmethod
    def _get_kernel_windows_cygwin():
        registry_key = (
            '/proc/registry/HKEY_LOCAL_MACHINE/'
            'SOFTWARE/Microsoft/Windows NT/CurrentVersion'
        )
        try:
            with open(
                    os.path.join(registry_key, 'CurrentVersion'),
                    errors='replace'
            ) as ifile:
                kernel = ifile.readline()
            with open(
                    os.path.join(registry_key, 'CurrentBuildNumber'),
                    errors='replace'
            ) as ifile:
                kernel += '.' + ifile.readline()
        except OSError:
            kernel = 'unknown'
        return kernel

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_kernel(cls):
        """
        Return kernel version (ie '4.5', '5.2')
        """
        system = cls.get_system()
        kernel = 'unknown'
        if system in ('linux', 'macos'):
            kernel = os.uname()[2]
        elif system == 'windows':
            if os.name == 'posix':
                kernel = cls._get_arch_windows_cygwin()
            else:
                kernel = platform.version()
        return kernel

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def get_system():
        """
        Return system name (ie 'linux', 'windows')
        """
        system = 'unknown'
        if os.name == 'nt':
            system = 'windows'
        else:
            osname = os.uname()[0]
            if osname == 'Linux':
                system = 'linux'
            elif osname == 'Darwin':
                system = 'macos'
            elif osname.startswith('cygwin'):
                system = 'windows'
        return system

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_arch(cls):
        """
        Return arch name (ie 'x86', 'x86_64')
        """
        system = cls.get_system()
        arch = 'unknown'
        if system == 'linux':
            arch = cls._get_arch_linux()
        elif system == 'macos':
            arch = cls._get_arch_macos()
        elif system == 'windows':
            if os.name == 'posix':
                arch = cls._get_arch_windows_cygwin()
            else:
                arch = cls._get_arch_windows()
        return arch

    @classmethod
    def get_platform(cls):
        """
        Return platform
       (ie linux-x86, linux-x86_64, macos-x86_64, windows-x86_64).
        """
        return cls.get_system() + '-' + cls.get_arch()


class _System(Platform):

    @staticmethod
    def _get_file_time(file):
        try:
            return os.stat(file)[8]
        except (OSError, TypeError):
            return 0

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

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_port_globs(_platform):
        """
        Return tuple of portname globs
        (ie 'linux64_*-x86*', 'windows64_*-x86*')
        """
        mapping = {
            'linux-x86_64': ('linux64_*-x86*', 'linux_*-x86*'),
            'linux-x86': ('linux_*-x86*'),
            'linux-sparc64': ('linux64_*-sparc64*', 'linux_*-sparc*'),
            'linux-power64': ('linux64_*-power64*', 'linux_*-power*'),
            'macos-x86_64': ('macos64_*-x86*', 'macos_*-x86*'),
            'macos-x86': ('macos_*-x86*'),
            'windows-x86_64': ('windows64_*-x86*', 'windows_*-x86*'),
            'windows-x86': ('windows_*-x86*')
        }

        try:
            return mapping[_platform]
        except KeyError:
            return {}


class CommandError(Exception):
    """
    Command module error.
    """


class CommandKeywordError(CommandError):
    """
    Command keyword error.
    """


class CommandNotFoundError(CommandError):
    """
    Command not found error.
    """


class ExecutableCallError(CommandError):
    """
    Executable call error.
    """


class GlibcVersionError(CommandError):
    """
    Command 'ldd' version found error.
    """


if __name__ == '__main__':
    help(__name__)
