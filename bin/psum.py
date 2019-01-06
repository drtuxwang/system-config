#!/usr/bin/env python3
"""
Calculate checksum lines using imagehash, file size and file modification time.
"""

import argparse
import glob
import logging
import os
import signal
import sys

import PIL
import imagehash

import command_mod
import file_mod
import logging_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")

MAX_DISTANCE_IDENTICAL = 6

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable=invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_update_file(self):
        """
        Return update file.
        """
        if self._args.update_file:
            return self._args.update_file[0]
        return None

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Calculate checksum lines using imagehash, file size '
            'and file modification time.'
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

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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

    def _calc(self, options, files):
        for file in files:
            if os.path.isdir(file) and os.path.basename(file) != '...':
                if not os.path.islink(file):
                    if options.get_recursive_flag():
                        try:
                            self._calc(options, sorted([
                                os.path.join(file, x)
                                for x in os.listdir(file)
                            ]))
                        except PermissionError:
                            pass
            elif os.path.isfile(file) and os.path.basename(file) != 'fsum':
                file_stat = file_mod.FileStat(file)
                try:
                    phash = self._cache[
                        (file, file_stat.get_size(), file_stat.get_time())]
                except KeyError:
                    try:
                        phash = str(imagehash.phash(PIL.Image.open(file)))
                    except OSError:
                        continue
                print("{0:s}/{1:010d}/{2:d}  {3:s}".format(
                    phash,
                    file_stat.get_size(),
                    file_stat.get_time(),
                    file
                ))

    @staticmethod
    def _show_same(phashes):
        found = False

        files = sorted(phashes)
        for i, file1 in enumerate(files):
            same_files = []
            phash = phashes[file1]
            for file2 in files[i+1:]:
                distance = format(phashes[file2] ^ phash, "08b").count('1')
                if distance < MAX_DISTANCE_IDENTICAL:
                    same_files.append(file2)

            if same_files:
                sorted_files = sorted([file1] + same_files)
                logger.warning(
                    "Identical: %s",
                    command_mod.Command.args2cmd(sorted_files),
                )
                found = True

        return found

    @classmethod
    def _check(cls, files):
        found = False

        for psumfile in files:
            phashes = {}
            try:
                with open(psumfile, errors='replace') as ifile:
                    for line in ifile:
                        line = line.rstrip('\r\n')
                        phash, _, _, file = cls._get_checksum(line)
                        phashes[file] = int(phash, 16)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + psumfile +
                    '" checksums file.'
                )

            found |= cls._show_same(phashes)

        if found:
            raise SystemExit(1)

    @staticmethod
    def _get_checksum(line):
        i = line.find('  ')
        try:
            checksum, size, mtime = line[:i].split('/')
            size = int(size)
            mtime = int(mtime)
            file = line[i+2:]
            return checksum, size, mtime, file
        except ValueError:
            return '', -1, -1, ''

    def _get_cache(self, update_file):
        if not os.path.isfile(update_file):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + update_file +
                '" checksum file.'
            )
        try:
            with open(update_file, errors='replace') as ifile:
                for line in ifile:
                    try:
                        line = line.rstrip('\r\n')
                        checksum, size, mtime, file = self._get_checksum(line)
                        if file:
                            self._cache[(file, size, mtime)] = checksum
                    except IndexError:
                        pass
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + update_file +
                '" checksum file.'
            )

    def run(self):
        """
        Start program
        """
        options = Options()

        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._cache = {}
            update_file = options.get_update_file()
            if update_file:
                self._get_cache(update_file)

            self._calc(options, options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
