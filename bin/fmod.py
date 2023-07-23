#!/usr/bin/env python3
"""
Set file access mode.
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import Any, List

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def get_fmod(self) -> int:
        """
        Return file permission mode.
        """
        return self._fmod

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_xmod(self) -> int:
        """
        Return executable permission mode.
        """
        return self._xmod

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Set file access mode.")

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Set mod of directories recursively.",
        )
        parser.add_argument(
            '-r',
            dest='mode',
            action='store_const', const='r',
            help="Set read-only permission for user.",
        )
        parser.add_argument(
            '-rg',
            dest='mode',
            action='store_const',
            const='rg',
            help="Set read-only permission for user and group.",
        )
        parser.add_argument(
            '-ra',
            dest='mode',
            action='store_const',
            const='ra',
            help="Set read-only permission for everyone.",
        )
        parser.add_argument(
            '-w',
            dest='mode',
            action='store_const',
            const='w',
            help="Set read-write permission for user."
        )
        parser.add_argument(
            '-wg',
            dest='mode',
            action='store_const',
            const='wg',
            help="Set read-write permission for user and read for group.",
        )
        parser.add_argument(
            '-wa',
            dest='mode',
            action='store_const',
            const='wa',
            help="Set read-write permission for user and read for others.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File or directory.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        mode = self._args.mode
        if mode == 'r':
            self._xmod = 0o500
            self._fmod = 0o400
        elif mode == 'rg':
            self._xmod = 0o550
            self._fmod = 0o440
        elif mode == 'ra':
            self._xmod = 0o555
            self._fmod = 0o444
        elif mode == 'w':
            self._xmod = 0o700
            self._fmod = 0o600
        elif mode == 'wg':
            self._xmod = 0o750
            self._fmod = 0o640
        elif mode == 'wa':
            self._xmod = 0o755
            self._fmod = 0o644
        else:
            self._xmod = 0o755
            self._fmod = 0o644


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def _chmod(path: Path, mod: int) -> None:
        fmod = file_mod.FileStat(path).get_mode() % 512
        if fmod != mod:
            print(f"{fmod:o}>{mod:o}: {path}")
            path.chmod(mod)

    @staticmethod
    def _setmod_link(path: Path) -> None:
        link_stat = file_mod.FileStat(path, follow_symlinks=False)
        file_stat = file_mod.FileStat(path)
        file_time = file_stat.get_time()

        if file_time != link_stat.get_time():
            print(f"<utime>: {path} -> {path.readlink()}")  # type: ignore
            try:
                os.utime(path, (file_time, file_time), follow_symlinks=False)
            except NotImplementedError:
                os.utime(path, (file_time, file_time))

    def _setmod_directory(self, path: Path) -> None:
        paths = list(path.iterdir())
        if self._recursive_flag:
            try:
                self._setmod(paths)
            except PermissionError:
                pass
        try:
            self._chmod(path, self._xmod)
        except OSError:
            print(f"Permission denied: {path}{os.sep}")
        if paths:
            file_stat = file_mod.FileStat(file_mod.FileUtil.newest(
                [str(x) for x in paths]
            ))
            file_time = file_stat.get_time()
            if file_time != file_mod.FileStat(path).get_time():
                print(f"<utime>: {path}/")
                try:
                    os.utime(path, (file_time, file_time))
                except OSError:
                    print(f"Permission denied: {path}{os.sep}")

    def _setmod_file(self, path: Path) -> None:
        try:
            try:
                with path.open('rb') as ifile:
                    magic = ifile.read(4)
            except OSError:
                path.chmod(self._fmod)
                with path.open('rb') as ifile:
                    magic = ifile.read(4)

            if (
                magic.startswith(b'#!') or
                magic in self._exe_magics or
                self._is_exe_ext.search(str(path))
            ):
                path.chmod(self._xmod)
            elif self._is_not_exe_ext.search(str(path)):
                path.chmod(self._fmod)
            elif os.access(path, os.X_OK):
                path.chmod(self._xmod)
            else:
                path.chmod(self._fmod)
        except OSError:
            print(f"Permission denied: {path}")

    def _setmod(self, paths: List[Path]) -> None:
        for path in sorted(paths):
            if path.is_symlink():
                self._setmod_link(path)
            elif path.is_dir():
                self._setmod_directory(path)
            elif path.is_file():
                self._setmod_file(path)
            else:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" file.',
                )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._exe_magics = (
            b'\177ELF',             # linux/sunos      (127  E   L   F )
            b'\312\376\272\276',    # macos-x86/x86_64 (202 254 186 190)
            b'\317\372\355\376',    # macos-x86_64     (207 250 237 254)
            b'\316\372\355\376',    # macos-x86        (206 250 237 254)
            b'MZ\220\000',          # windows          ( M   Z  144  0 )
        )
        self._is_exe_ext = re.compile(
            '[.](bat|cmd|com|dll|exe|ms[ip]|psd|sfx|s[olh]|s[ol][.].*|tcl)$',
            re.IGNORECASE
        )
        self._is_not_exe_ext = re.compile(
            '[.](7z|[acfo]|ace|asr|avi|bak|bmp|bz2|ce?rt|cfg|cpp|css|dat|deb|'
            'diz|doc|docx|egg|f77|f90|gif|gm|gz|h|hlp|htm|html|ico|ini|'
            'installed|ism|iso|jar|java|jpe?g|js|json|key|lic|lib|list|log|'
            'mov|mp[34g]|mpeg|o|obj|od[fgst]|ogg|opt|pk|pdf|png|ppt|pptx|rar|'
            'reg|rpm|swf|tar([.].*)?|txt|url|wav|whl|wsdl|xhtml|xls|xlsx|xml|'
            'xs[dl]|xvid|ya?ml|zip)$',
            re.IGNORECASE
        )

        self._recursive_flag = options.get_recursive_flag()
        self._fmod = options.get_fmod()
        self._xmod = options.get_xmod()

        self._setmod([Path(x) for x in options.get_files()])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
