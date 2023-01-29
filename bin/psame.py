#!/usr/bin/env python3
"""
Show picture files with same finger print.
"""

import argparse
import itertools
import logging
import os
import signal
import sys
from pathlib import Path
from typing import List, Set

import imagehash  # type: ignore
import PIL  # type: ignore
import pybktree  # type: ignore

import command_mod
import logging_mod

MAX_DISTANCE_IDENTICAL = 6

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
        return self._args.files

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Show picture files with same finger print.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file|directory',
            help="File or directory containing files to compare",
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

    def _calc(self, options: Options, paths: List[Path]) -> dict:
        image_phash = {}

        for path in paths:
            if path.is_dir():
                if options.get_recursive_flag() and not path.is_symlink():
                    try:
                        image_phash.update(self._calc(
                            options,
                            sorted(path.iterdir()),
                        ))
                    except PermissionError:
                        pass
            elif path.is_file():
                try:
                    phash = int(str(imagehash.phash(PIL.Image.open(path))), 16)
                except OSError:
                    continue
                image_phash[path] = phash

        return image_phash

    @staticmethod
    def _match(image_phash: dict) -> Set[str]:
        """
        Using BKTree to speed up check:
        if phash1 - phash2 <= MAX_DISTANCE_IDENTICAL:
        """
        phash_images: dict = {}
        for image, phash in image_phash.items():
            if phash in phash_images:
                phash_images[phash].append(image)
            else:
                phash_images[phash] = [image]

        matched_images: set = set()
        tree = pybktree.BKTree(pybktree.hamming_distance, phash_images)
        for phash in sorted(phash_images):
            images = frozenset(itertools.chain.from_iterable([
                phash_images[match]
                for _, match in tree.find(phash, MAX_DISTANCE_IDENTICAL)
            ]))
            if len(images) > 1:
                matched_images.add(images)

        return matched_images

    def run(self) -> bool:
        """
        Start program
        """
        options = Options()

        image_phash = self._calc(options, [
            Path(x) for x in options.get_files()]
        )
        matched_images = self._match(image_phash)

        for images in sorted(matched_images):
            logger.warning(
                "Identical: %s",
                command_mod.Command.args2cmd(sorted(images)),
            )
        return bool(matched_images)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
