#!/usr/bin/env python3
"""
Calculate checksum using SHA512, file size and file modification time.
"""

import argparse
import hashlib
import os
import signal
import sys
from pathlib import Path
from typing import List, Tuple

from file_mod import FileStat


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_check_flag(self) -> bool:
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_create_flag(self) -> bool:
        """
        Return create flag.
        """
        return self._args.create_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return [os.path.expandvars(x) for x in self._args.files]

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_update_file(self) -> str:
        """
        Return update file.
        """
        if self._args.update_file:
            return self._args.update_file[0]
        return None

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Calculate checksum using MD5, file size and "
            "file modification time.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help="Check checksums against files.",
        )
        parser.add_argument(
            '-f',
            dest='create_flag',
            action='store_true',
            help='Create ".fsum" file for each file.',
        )
        parser.add_argument(
            '-update',
            nargs=1,
            dest='update_file',
            metavar='index.fsum',
            help="Update checksums if file size and date changed.",
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file|file.fsum',
            help='File to checksum or ".fsum" checksum file.',
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    @staticmethod
    def _md5sum(path: Path) -> str:
        md5 = hashlib.md5()
        try:
            with path.open('rb') as ifile:
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (OSError, TypeError):
            print(f'{sys.argv[0]}: Cannot read "{path}" file', file=sys.stderr)
        return md5.hexdigest()

    @staticmethod
    def _sha512sum(path: Path) -> str:
        sha512 = hashlib.sha512()
        try:
            with path.open('rb') as ifile:
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    sha512.update(chunk)
        except (OSError, TypeError):
            print(f'{sys.argv[0]}: Cannot read "{path}" file', file=sys.stderr)
        return f'sha512:{sha512.hexdigest()}'

    @staticmethod
    def _get_files(directory_path: Path) -> List[Path]:
        try:
            paths = list(directory_path.iterdir())
            if directory_path.name == '...':
                paths = [
                    x
                    for x in directory_path.iterdir()
                    if not str(x).startswith('.')
                ]
        except PermissionError:
            pass

        return paths

    def _calc(self, options: Options, paths: List[Path]) -> None:
        for path in paths:
            if str(path).endswith('..fsum'):
                self._get_cache(path)
            elif path.is_dir():
                if not path.is_symlink():
                    if options.get_recursive_flag():
                        self._calc(options, sorted(self._get_files(path)))
            elif path.is_file() and not path.is_symlink():
                file_stat = FileStat(path)
                try:
                    checksum = self._cache[(
                        str(path),
                        file_stat.get_size(),
                        int(file_stat.get_mtime()),
                    )]
                except KeyError:
                    checksum = self._sha512sum(path)
                if not checksum:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{path}" file.',
                    )
                print(
                    f"{checksum}/"
                    f"{file_stat.get_size():010d}/"
                    f"{int(file_stat.get_mtime())}  "
                    f"{path}",
                )
                if options.get_create_flag():
                    fsum_path = Path(f'{path}.fsum')
                    try:
                        with fsum_path.open('w') as ofile:
                            print(
                                f"{checksum}/"
                                f"{file_stat.get_size():010d}/"
                                f"{int(file_stat.get_mtime())}  "
                                f"{path.name}",
                                file=ofile,
                            )
                        file_time = file_stat.get_mtime()
                        os.utime(fsum_path, (file_time, file_time))
                    except OSError as exception:
                        raise SystemExit(
                            f'{sys.argv[0]}: Cannot create '
                            f'"{fsum_path}" file.',
                        ) from exception

    @classmethod
    def _isdiff(cls, checksum: str, path: Path) -> bool:
        if checksum.startswith('sha512:'):
            if cls._sha512sum(path) != checksum:
                return True
        elif len(checksum) == 32:
            if cls._md5sum(path) != checksum:
                return True
        return False

    def _check(self, files: List[str]) -> None:
        found = []
        nfail = 0
        nmiss = 0

        for fsum_path in [Path(x) for x in files]:
            found.append(str(fsum_path))
            directory = fsum_path.parent
            try:
                with fsum_path.open(errors='replace') as ifile:
                    for line in ifile:
                        line = line.rstrip('\n')
                        checksum, size, mtime, file = self._get_checksum(line)
                        file = f'{directory}/{file}'
                        found.append(file)
                        file_stat = FileStat(file)
                        try:
                            if not Path(file).is_file():
                                print(f'{file} # FAILED open or read')
                                nmiss += 1
                            elif size != file_stat.get_size():
                                print(f'{file} # FAILED checksize')
                                nfail += 1
                            elif mtime != int(file_stat.get_mtime()):
                                print(f'{file} # FAILED checkdate')
                                nfail += 1
                            elif self._isdiff(checksum, Path(file)):
                                print(f'{file} # FAILED checksum')
                                nfail += 1
                        except TypeError as exception:
                            raise SystemExit(
                                f'{sys.argv[0]}: Corrupt '
                                f'"{fsum_path}" checksum file.',
                            ) from exception
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read "{fsum_path}" checksum file.',
                ) from exception

        if f'{directory}/index.fsum' in files:
            for file in self._extra(directory, found):
                print(file, '# EXTRA file found')
        if nmiss > 0:
            print(f"fsum: Cannot find {nmiss} of {len(found)} listed files.")
        if nfail > 0:
            print(
                f"fsum: Mismatch in {nfail} of "
                f"{len(found) - nmiss} computed checksums.",
            )

    def _extra(self, directory_path: Path, found: List[str]) -> List[str]:
        extra = []
        try:
            paths = (
                list(directory_path.iterdir())
                if directory_path
                else [Path(x) for x in os.listdir()]
            )
        except PermissionError:
            pass
        else:
            for path in paths:
                if path.is_dir():
                    if not path.is_symlink():
                        extra.extend(self._extra(path, found))
                elif (
                    not path.is_symlink() and
                    str(path) not in found and
                    path.suffix != '.fsum'
                ):
                    extra.append(str(path))
        return extra

    @staticmethod
    def _get_checksum(line: str) -> Tuple[str, int, int, str]:
        i = line.find('  ')
        try:
            checksum, size, mtime = line[:i].split('/')
            file = line[i+2:]
            return checksum, int(size), int(mtime), file
        except ValueError:
            return '', -1, -1, ''

    def _get_cache(self, cache_path: Path) -> None:
        if not cache_path.is_file():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{cache_path}" checksum file.',
            )

        directory_path = cache_path.parent
        try:
            with cache_path.open(errors='replace') as ifile:
                for line in ifile:
                    try:
                        line = line.rstrip('\n')
                        checksum, size, mtime, file = self._get_checksum(line)
                        path = Path(directory_path, file)
                        if (file, size, mtime) not in self._cache:
                            self._cache[(file, size, mtime)] = checksum
                    except IndexError:
                        pass
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" checksum file.',
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._cache: dict = {}
            update_file = options.get_update_file()
            if update_file:
                self._get_cache(Path(update_file))

            self._calc(options, [Path(x) for x in options.get_files()])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
