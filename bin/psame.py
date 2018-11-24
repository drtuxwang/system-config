#!/usr/bin/env python3
"""
Show picture files with same finger print.
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
import logging_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

MAX_DISTANCE_IDENTICAL = 21

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable=invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options(object):
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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show picture files with same finger print.')

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|directory',
            help='File or directory containing files to compare'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main(object):
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

    def _ahash_check(self, options, files):
        for file in files:
            if os.path.isdir(file):
                if not os.path.islink(file) and options.get_recursive_flag():
                    try:
                        self._ahash_check(options, sorted([
                            os.path.join(file, x)
                            for x in os.listdir(file)
                        ]))
                    except PermissionError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot open "' +
                            file + '" directory.'
                        )
            elif os.path.isfile(file):
                try:
                    ahash = imagehash.average_hash(PIL.Image.open(file))
                except OSError:
                    continue
                if ahash in self._ahashfiles:
                    self._ahashfiles[ahash].add(file)
                else:
                    self._ahashfiles[ahash] = set([file])

    @staticmethod
    def _phash_check(files):
        phashes = {
            file: imagehash.phash(PIL.Image.open(file))
            for file in files
        }

        for i, file1 in enumerate(files):
            same_files = []
            phash = phashes[file1]
            for file2 in files[i+1:]:
                if phashes[file2] - phash <= MAX_DISTANCE_IDENTICAL:
                    same_files.append(file2)
            if same_files:
                return [file1] + same_files
        return []

    def run(self):
        """
        Start program
        """
        options = Options()

        self._ahashfiles = {}
        files = []
        for file in options.get_files():
            if os.path.isdir(file):
                files.extend(sorted(
                    [os.path.join(file, x) for x in os.listdir(file)]
                ))
            else:
                files.append(file)
        self._ahash_check(options, files)

        exitcode = 0
        for files in sorted(self._ahashfiles.values()):
            if len(files) > 1:
                sorted_files = self._phash_check(sorted(files))
                if sorted_files:
                    logger.warning(
                        "Identical: %s",
                        command_mod.Command.args2cmd(sorted_files),
                    )
                    exitcode = 1
        return exitcode


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
