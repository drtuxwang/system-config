#!/usr/bin/env python3
"""
Python command handling module

Copyright GPL v2: 2006-2024 By Dr Colin Kong
"""

import functools
import glob
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Sequence, Union

RELEASE = '2.7.0'
VERSION = 20240509


class Command:
    """
    This class stores a command (uses supplied executable)
    """

    def __init__(self, program: Union[str, Path], **kwargs: Any) -> None:
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
        self._args = [self._locate(str(program), info)]
        try:
            self._args.extend([str(x) for x in kwargs['args']])
        except KeyError:
            pass

    @staticmethod
    def _parse_keys(keys: Sequence[str], **kwargs: Any) -> dict:
        if set(kwargs.keys()) - set(keys):
            raise CommandKeywordError(
                'Unsupported keyword '
                f'"{list(set(kwargs.keys()) - set(keys))[0]}".',
            )
        info: dict = {}
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
    def _locate(cls, program: str, info: dict) -> str:
        _platform = info['platform']
        if not _platform:
            _platform = _System.get_platform()
        extensions = cls._get_extensions(_platform)

        directory_path = (
            Path(info['directory'])
            if info['directory']
            else Path(sys.argv[0]).resolve().parent
        )
        if directory_path.name == 'bin':
            directory_path = directory_path.parent
            path = cls._search_ports(
                directory_path,
                _platform,
                program,
                extensions,
            )
            if path:
                return str(path)

        path = cls._search_path(
            [str(x) for x in info['pathextra']],
            program,
            extensions,
        )
        if path:
            return str(path)

        if info['errors'] == 'stop':
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find required "{program}" software.',
            )
        if info['errors'] == 'ignore':
            return ''
        raise CommandNotFoundError(
            f'Cannot find required "{program}" software.',
        )

    @staticmethod
    def _get_extensions(_platform: str) -> List[str]:
        extensions = ['']
        if _platform.startswith('windows-'):
            try:
                extensions.extend(
                    os.environ['PATHEXT'].lower().split(os.pathsep))
            except KeyError:
                pass
        return extensions

    @classmethod
    def _check_glibc(cls, paths: List[Path]) -> List[Path]:
        has_glibc = re.compile(r'-glibc_\d+[.]\d+([.]\d+)?')
        paths_new = []
        for path in paths:
            if has_glibc.search(str(path)):
                version = str(
                    path
                ).split('-glibc_')[1].split('-')[0].split('/')[0]
                if LooseVersion(_System.get_glibc()) >= LooseVersion(version):
                    paths_new.append(path)
            else:
                paths_new.append(path)
        return paths_new

    @classmethod
    def _search_ports(
        cls,
        path: Path,
        _platform: str,
        program: str,
        extensions: List[str],
    ) -> Path:
        paths = []
        for port_glob in _System.get_port_globs(_platform):
            for extension in extensions:
                paths = (
                    list(path.glob(f'*/*{port_glob}/{program}{extension}')) +
                    list(path.glob(f'*{port_glob}/{program}{extension}'))
                )
                if _platform.startswith('linux'):
                    paths = cls._check_glibc(paths)
                if paths:
                    return _System.newest(paths)

        # Search directories with 4 or more char as fall back for local port
        if not paths:
            isport = re.compile('-.*_.*-.*_')
            for extension in extensions:
                paths = [
                    x
                    for x in path.glob(f'????*/{program}{extension}')
                    if not isport.search(str(x))
                ]
                if paths:
                    break
        if paths:
            return _System.newest(paths)

        return None

    @staticmethod
    def _search_path(
        pathextra: List[str],
        program: str,
        extensions: List[str],
    ) -> Path:
        program = Path(program).name

        # Shake PATH to make it unique
        directories = []
        for directory in (
            list(pathextra) + os.environ['PATH'].split(os.pathsep)
        ):
            if directory:
                if directory not in directories:
                    directories.append(directory)

        # Prevent recursion
        if (
            not pathextra and
            Path(sys.argv[0]).name in (program, f'{program}.py')
        ):
            mydir = str(Path(sys.argv[0]).parent)
            if mydir in directories:
                directories = directories[directories.index(mydir) + 1:]

        mynames = (
            (sys.argv[0][:-3], sys.argv[0])
            if sys.argv[0].endswith('.py')
            else (sys.argv[0], f'{sys.argv[0]}.py')
        )

        for directory in directories:
            if Path(directory).is_dir():
                for extension in extensions:
                    path = Path(directory, program + extension)
                    if path.is_file():
                        if str(path) not in mynames:
                            return path

        return None

    @staticmethod
    def args2cmd(args: list) -> str:
        """
        Join list of arguments into a command string.

        args = List of arguments

        subprocess.list2cmdline() does not handle "&" properly)
        """
        nargs = []
        for arg in [str(x) for x in args]:
            for char in '"\' &;':
                if char in arg and arg != ';':
                    quoted = arg.replace('\\', '\\\\').replace('"', '\\"')
                    nargs.append(f'"{quoted}"')
                    break
            else:
                nargs.append(arg)
        return ' '.join(nargs)

    @staticmethod
    def _cmd2chars(cmd: str) -> List[str]:
        chars: list = []
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
    def _chars2args(chars: List[str]) -> List[str]:
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
    def cmd2args(cls, cmd: str) -> List[str]:
        """
        Split a command string into a list of arguments.
        """
        chars = cls._cmd2chars(cmd)
        args = cls._chars2args(chars)
        return args

    def get_cmdline(self) -> List[str]:
        """
        Return the command line as a list.
        """
        return self._args

    def get_file(self) -> str:
        """
        Return file location.
        """
        return self._args[0]

    def get_args(self) -> List[str]:
        """
        Return list of arguments.
        """
        return self._args[1:]

    def append_arg(self, arg: Any) -> None:
        """
        Append to command line arguments

        arg = Argument
        """
        self._args.append(str(arg))

    def extend_args(self, args: list) -> None:
        """
        Extend command line arguments

        args = List of arguments
        """
        self._args.extend([str(x) for x in args])

    def set_args(self, args: list) -> None:
        """
        Set command line arguments

        args = List of arguments
        """
        self._args[1:] = [str(x) for x in args]

    def is_found(self) -> bool:
        """
        Return True if file is defined.
        """
        return self._args[0] != ''


class CommandFile(Command):
    """
    This class stores a command (uses supplied executable location)
    """

    @staticmethod
    def _locate(program: str, info: dict) -> str:
        if Path(program).is_file():
            return program

        if info['errors'] == 'stop':
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find required "{program}" software.',
            )
        if info['errors'] == 'ignore':
            return ''
        raise CommandNotFoundError(
            f'Cannot find required "{program}" software.',
        )


class LooseVersion:
    """
    This class store version as sortable tokens.

    1.1 < 1.2b2 < 1.2rc1 < 1.2 < 1.2+git20220418 < 1.2-2 < 1.2.1 < 1.2a < 1.10
    """

    def __init__(self, version: str) -> None:
        self._version = version
        tokens = re.split(r'([\D]+)', '• '+version.lower())[1:]
        tokens = [' '+x if x.isalpha() else x for x in tokens]
        if tokens[-1] == '':
            tokens[-2] = tokens[-2][1:]

        self._tokens = [int(x) if x.isdigit() else x for x in tokens] + [' •']

    def get_version(self) -> str:
        """
        Return version.
        """
        return self._version

    def get_tokens(self) -> list:
        """
        Return version tokens.
        """
        return self._tokens

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LooseVersion):
            return NotImplemented
        return self.get_tokens() < other.get_tokens()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, LooseVersion):
            return NotImplemented
        return self.get_tokens() <= other.get_tokens()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LooseVersion):
            return NotImplemented
        return self.get_tokens() == other.get_tokens()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, LooseVersion):
            return NotImplemented
        return self.get_tokens() >= other.get_tokens()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, LooseVersion):
            return NotImplemented
        return self.get_tokens() > other.get_tokens()


class Platform:
    """
    This class provides some platform information
    """

    @staticmethod
    def _get_arch_linux() -> str:
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
    def _get_arch_macos() -> str:
        # "/usr/sbin/sysct -a" => "hw.cpu64bit_capable: 1"
        machine = os.uname()[-1]
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine == 'i386':
            arch = 'x86'
        return arch

    @staticmethod
    def _get_arch_windows() -> str:
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
    def _get_arch_windows_cygwin() -> str:
        osname, *_, machine = os.uname()
        arch = 'unknown'
        if machine == 'x86_64':
            arch = 'x86_64'
        elif machine.endswith('86'):
            arch = 'x86_64' if 'WOW64' in osname else 'x86'
        return arch

    @staticmethod
    def _locate_program(program: str) -> str:
        for directory in os.environ['PATH'].split(os.pathsep):
            path = Path(directory, program)
            if path.is_file():
                break
        else:
            raise CommandNotFoundError(
                f'Cannot find required "{program}" software.',
            )
        return str(path)

    @classmethod
    def _run_program(cls, command: List[str]) -> List[str]:
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        lines = []
        try:
            with subprocess.Popen(
                [program] + command[1:],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as child:
                while True:
                    try:
                        bline = child.stdout.readline()
                    except (KeyboardInterrupt, OSError):
                        break
                    if not bline:
                        break
                    line = bline.decode(errors='replace')
                    lines.append(line.rstrip('\n'))
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{program}" program.',
            ) from exception
        return lines

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_glibc(cls) -> str:
        """
        Return glibc version string
        (based on glibc version used to compile 'ldd' or
        return '0.0' for non Linux)
        """
        if cls.get_platform().startswith('linux'):
            lines = cls._run_program(['ldd', '--version'])
            try:
                for line in lines:
                    if 'GLIBC' in line:
                        return line.split()[-1]
            except IndexError as exception:
                raise GlibcVersionError(
                    'Cannot determine "glibc" version.'
                ) from exception
        return '0.0'

    @staticmethod
    def _get_kernel_windows_cygwin() -> str:
        registry_key = (
            '/proc/registry/HKEY_LOCAL_MACHINE/'
            'SOFTWARE/Microsoft/Windows NT/CurrentVersion'
        )
        try:
            path = Path(registry_key, 'CurrentVersion')
            with path.open(errors='replace') as ifile:
                kernel = ifile.readline()
            path = Path(registry_key, 'CurrentBuildNumber')
            with path.open(errors='replace') as ifile:
                kernel += f'.{ifile.readline()}'
        except OSError:
            kernel = 'unknown'
        return kernel

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_kernel(cls) -> str:
        """
        Return kernel version (ie '4.5', '5.2')
        """
        system = cls.get_system()
        kernel = 'unknown'
        if system in ('linux', 'macos'):
            kernel = os.uname()[2]
        elif system == 'windows':
            kernel = (
                cls._get_arch_windows_cygwin()
                if os.name == 'posix'
                else platform.version()
            )
        return kernel

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def get_system() -> str:
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
    def get_arch(cls) -> str:
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
            arch = (
                cls._get_arch_windows_cygwin()
                if os.name == 'posix'
                else cls._get_arch_windows()
            )
        return arch

    @classmethod
    def get_platform(cls) -> str:
        """
        Return platform
        (ie linux-x86, linux-x86_64, macos-x86_64, windows-x86_64).
        """
        return f'{cls.get_system()}-{cls.get_arch()}'


class _System(Platform):

    @staticmethod
    def _get_file_time(file: Path) -> int:
        try:
            return int(file.stat()[8])
        except (OSError, TypeError):
            return 0

    @classmethod
    def newest(cls, paths: List[Path]) -> Path:
        """
        Return newest file or directory.

        files = List of files
        """
        path_new = None
        new_time = -1

        for path in paths:
            if path.is_file() or path.is_dir():
                file_time = cls._get_file_time(path)
                if file_time > new_time:
                    path_new = path
                    new_time = file_time

        return path_new

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_port_globs(_platform: str) -> Sequence[str]:
        """
        Return tuple of portname globs
        (ie 'linux64_*-x86*', 'windows64_*-x86*')
        """
        mapping = {
            'linux-x86_64': ('linux64_*-x86*', 'linux_*-x86*'),
            'linux-x86': ('linux_*-x86*',),
            'linux-sparc64': ('linux64_*-sparc64*', 'linux_*-sparc*'),
            'linux-power64': ('linux64_*-power64*', 'linux_*-power*'),
            'macos-x86_64': ('macos64_*-x86*', 'macos_*-x86*'),
            'macos-x86': ('macos_*-x86*',),
            'windows-x86_64': ('windows64_*-x86*', 'windows_*-x86*'),
            'windows-x86': ('windows_*-x86*',)
        }

        return mapping.get(_platform, [])


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
    if sys.argv[-1] in ['-v', '-V', '-version', '--version']:
        print(f"Python command handling module {RELEASE} ({VERSION})")
    else:
        help(__name__)
