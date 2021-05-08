#!/usr/bin/env python3
"""
Calculate checksum using MD5, file size and file modification time.
"""

import argparse
import glob
import hashlib
import os
import signal
import sys
from typing import List, Tuple

import file_mod


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
        return self._args.files

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
            description='Calculate checksum using MD5, file size and '
            'file modification time.',
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help='Check checksums against files.'
        )
        parser.add_argument(
            '-f',
            dest='create_flag',
            action='store_true',
            help='Create ".fsum" file for each file.'
        )
        parser.add_argument(
            '-update',
            nargs=1,
            dest='update_file',
            metavar='index.fsum',
            help='Update checksums if file size and date changed.'
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file|file.fsum',
            help='File to checksum or ".fsum" checksum file.'
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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def _md5sum(file: str) -> str:
        try:
            with open(file, 'rb') as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (OSError, TypeError) as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.'
            ) from exception
        return md5.hexdigest()

    def _calc(self, options: Options, files: List[str]) -> None:
        for file in files:
            if file.endswith('.../fsum'):
                self._get_cache(file)
            elif os.path.isdir(file):
                if not os.path.islink(file):
                    if options.get_recursive_flag():
                        try:
                            self._calc(options, sorted([
                                os.path.join(file, x)
                                for x in os.listdir(file)
                            ]))
                        except PermissionError:
                            pass
            elif os.path.isfile(file) and not os.path.islink(file):
                file_stat = file_mod.FileStat(file)
                try:
                    md5sum = self._cache[
                        (file, file_stat.get_size(), file_stat.get_time())]
                except KeyError:
                    md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" file.')
                print("{0:s}/{1:010d}/{2:d}  {3:s}".format(
                    md5sum,
                    file_stat.get_size(),
                    file_stat.get_time(),
                    file
                ))
                if options.get_create_flag():
                    try:
                        with open(file + '.fsum', 'w', newline='\n') as ofile:
                            print("{0:s}/{1:010d}/{2:d}  {3:s}".format(
                                md5sum,
                                file_stat.get_size(),
                                file_stat.get_time(),
                                os.path.basename(file)
                            ), file=ofile)
                        file_stat = file_mod.FileStat(file)
                        os.utime(
                            file + '.fsum',
                            (file_stat.get_time(), file_stat.get_time())
                        )
                    except OSError as exception:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + file +
                            '.fsum" file.'
                        ) from exception

    def _check(self, files: List[str]) -> None:
        found = []
        nfail = 0
        nmiss = 0

        for fsumfile in files:
            found.append(fsumfile)
            directory = os.path.dirname(fsumfile)
            try:
                with open(fsumfile, errors='replace') as ifile:
                    for line in ifile:
                        line = line.rstrip('\r\n')
                        md5sum, size, mtime, file = self._get_checksum(line)
                        file = os.path.join(directory, file)
                        found.append(file)
                        file_stat = file_mod.FileStat(file)
                        try:
                            if not os.path.isfile(file):
                                print(file, '# FAILED open or read')
                                nmiss += 1
                            elif size != file_stat.get_size():
                                print(file, '# FAILED checksize')
                                nfail += 1
                            elif self._md5sum(file) != md5sum:
                                print(file, '# FAILED checksum')
                                nfail += 1
                            elif mtime != file_stat.get_time():
                                print(file, '# FAILED checkdate')
                                nfail += 1
                        except TypeError as exception:
                            raise SystemExit(
                                sys.argv[0] + ': Corrupt "' + fsumfile +
                                '" checksum file.'
                            ) from exception
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + fsumfile +
                    '" checksum file.'
                ) from exception

        if os.path.join(directory, 'index.fsum') in files:
            for file in self._extra(directory, found):
                print(file, '# EXTRA file found')
        if nmiss > 0:
            print("fsum: Cannot find {0:d} of {1:d} listed files.".format(
                nmiss,
                len(found)
            ))
        if nfail > 0:
            print(
                "fsum: Mismatch in {0:d} of {1:d} computed checksums.".format(
                    nfail,
                    len(found) - nmiss
                )
            )

    def _extra(self, directory: str, found: List[str]) -> List[str]:
        extra = []
        try:
            if directory:
                files = [
                    os.path.join(directory, x)
                    for x in os.listdir(directory)
                ]
            else:
                files = [os.path.join(directory, x) for x in os.listdir()]
        except PermissionError:
            pass
        else:
            for file in files:
                if os.path.isdir(file):
                    if not os.path.islink(file):
                        extra.extend(self._extra(file, found))
                elif file not in found:
                    if not file.endswith('..fsum'):
                        extra.append(file)
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

    def _get_cache(self, update_file: str) -> None:
        if not os.path.isfile(update_file):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + update_file +
                '" checksum file.'
            )
        directory = os.path.dirname(update_file)
        try:
            with open(update_file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        line = line.rstrip('\r\n')
                        checksum, size, mtime, file = self._get_checksum(line)
                        file = os.path.join(directory, file)
                        file = file.replace('/.../../', '/')
                        if (file, size, mtime) not in self._cache:
                            self._cache[(file, size, mtime)] = checksum
                    except IndexError:
                        pass
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + update_file +
                '" checksum file.'
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
                self._get_cache(update_file)

            self._calc(options, options.get_files())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
