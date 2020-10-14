#!/usr/bin/env python3
"""
Show files with same MD5 checksums.
"""

import argparse
import glob
import hashlib
import logging
import os
import signal
import sys

import logging_mod
import command_mod

# pylint: disable = invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable = invalid-name
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

    def get_remove_flag(self):
        """
        Return remove flag.
        """
        return self._args.remove_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show files with same MD5 checksums.')

        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help='Delete all extra copies of duplicated files.'
        )
        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|file.md5',
            help='File to checksum or ".md5" checksum file.'
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
            if os.path.isdir(file):
                if not os.path.islink(file) and options.get_recursive_flag():
                    try:
                        self._calc(options, sorted([
                            os.path.join(file, x)
                            for x in os.listdir(file)
                        ]))
                    except PermissionError as exception:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot open "' +
                            file + '" directory.'
                        ) from exception
            elif os.path.isfile(file):
                md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" file.')
                if md5sum in self._md5files:
                    self._md5files[md5sum].add(file)
                else:
                    self._md5files[md5sum] = set([file])

    @staticmethod
    def _md5sum(file):
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

    @staticmethod
    def _remove(files):
        for file in files:
            print('  Removing "{0:s}" duplicated file'.format(file))
            try:
                os.remove(file)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' + file + '" file.'
                ) from exception

    def run(self):
        """
        Start program
        """
        options = Options()

        self._md5files = {}
        files = []
        for file in options.get_files():
            if os.path.isdir(file):
                files.extend(sorted(
                    [os.path.join(file, x) for x in os.listdir(file)]
                ))
            else:
                files.append(file)
        self._calc(options, files)

        exitcode = 0
        for files in sorted(self._md5files.values()):
            if len(files) > 1:
                sorted_files = sorted(files)
                logger.warning(
                    "Identical: %s",
                    command_mod.Command.args2cmd(sorted_files)
                )
                if options.get_remove_flag():
                    self._remove(sorted_files[1:])
                else:
                    exitcode = 1
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
