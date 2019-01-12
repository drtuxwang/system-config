#!/usr/bin/env python3
"""
Show picture files with same finger print.
"""

import argparse
import glob
import itertools
import logging
import os
import signal
import sys

import imagehash
import PIL
import pybktree

import command_mod
import logging_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

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
        image_phash = {}

        for file in files:
            if os.path.isdir(file):
                if options.get_recursive_flag() and not os.path.islink(file):
                    try:
                        image_phash.update(self._calc(options, sorted([
                            os.path.join(file, x)
                            for x in os.listdir(file)
                        ])))
                    except PermissionError:
                        pass
            elif os.path.isfile(file):
                try:
                    phash = int(str(imagehash.phash(PIL.Image.open(file))), 16)
                except OSError:
                    continue
                image_phash[file] = phash

        return image_phash

    @staticmethod
    def _match(image_phash):
        """
        Using BKTree to speed up check:
        if phash1 - phash2 <= MAX_DISTANCE_IDENTICAL:
        """
        phash_images = {}
        for image, phash in image_phash.items():
            if phash in phash_images:
                phash_images[phash].append(image)
            else:
                phash_images[phash] = [image]

        matched_images = set()
        tree = pybktree.BKTree(pybktree.hamming_distance, phash_images)
        for phash in sorted(phash_images):
            images = frozenset(itertools.chain.from_iterable([
                phash_images[match]
                for _, match in tree.find(phash, MAX_DISTANCE_IDENTICAL)
            ]))
            if len(images) > 1:
                matched_images.add(images)

        return matched_images

    def run(self):
        """
        Start program
        """
        options = Options()

        image_phash = self._calc(options, options.get_files())
        matched_images = self._match(image_phash)

        for images in sorted(matched_images):
            logger.warning(
                "Identical: %s",
                command_mod.Command.args2cmd(sorted(images)),
            )
        return matched_images != []


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
