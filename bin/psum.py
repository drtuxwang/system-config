#!/usr/bin/env python3
"""
Calculate checksum lines using imagehash, file size and file modification time.
"""

import argparse
import itertools
import logging
import os
import signal
import sys
from pathlib import Path
from typing import List, Set, Tuple

# pylint: disable=import-error
import imagehash  # type: ignore
import PIL  # type: ignore
import pybktree  # type: ignore
import pyzstd

from command_mod import Command
from file_mod import FileStat
from logging_mod import ColoredFormatter

MAX_DISTANCE_IDENTICAL = 6

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
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

    def get_update_file(self) -> str:
        """
        Return update file.
        """
        if self._args.update_file:
            return self._args.update_file[0]
        return ''

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Calculate checksum lines using imagehash, file size "
            "and file modification time.",
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            '-update',
            nargs=1,
            dest='update_file',
            metavar='index.psum.zst',
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
    def _get_checksum(line: str) -> Tuple[str, int, int, str]:
        i = line.find('  ')
        try:
            checksum, size, mtime = line[:i].split('/')
            file = line[i+2:]
            return checksum, int(size), int(mtime), file
        except ValueError:
            return '', -1, -1, ''

    @classmethod
    def _read(cls, path: Path) -> dict:
        logger.info("Reading checksum file: %s", path)
        if not path.is_file():
            raise SystemExit(
                f"{sys.argv[0]}: Cannot find checksum file: {path}",
            )

        images_phashes = {}
        try:
            with pyzstd.open(path, 'rt', errors='replace') as ifile:
                for line in ifile:
                    try:
                        line = line.rstrip('\n')
                        checksum, size, mtime, file = cls._get_checksum(line)
                        if file:
                            images_phashes[(file, size, mtime)] = checksum
                    except IndexError:
                        pass
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot read checksum file: {path}",
            ) from exception
        return images_phashes

    @classmethod
    def _update(
        cls,
        phashes: dict,
        recursive: bool,
        paths: List[Path],
    ) -> dict:
        logger.info("Updating checksums...")
        new_phashes = {}
        for path in paths:
            if path.is_dir():
                if recursive and not path.is_symlink():
                    try:
                        new_phashes.update(cls._update(
                            phashes,
                            recursive,
                            sorted(path.iterdir()),
                        ))
                    except PermissionError:
                        pass
            elif path.is_file():
                file_stat = FileStat(path)
                key = (str(path), file_stat.get_size(), file_stat.get_time())
                if key in phashes:
                    phash = phashes[key]
                else:
                    try:
                        phash = str(imagehash.phash(PIL.Image.open(path)))
                    except OSError:
                        continue
                new_phashes[key] = phash

        return new_phashes

    @classmethod
    def _check(cls, image_phashes: dict, new_phashes: Set[str]) -> None:
        """
        Using BKTree to speed up check:
        if phash1 - phash2 <= MAX_DISTANCE_IDENTICAL:
        """
        logger.info("Checking checksums...")

        phash_images: dict = {}
        for key, value in image_phashes.items():
            phash = int(value, 16)
            file, _, _ = key
            if phash in phash_images:
                phash_images[phash].append(file)
            else:
                phash_images[phash] = [file]

        matched_images = set()
        tree = pybktree.BKTree(pybktree.hamming_distance, phash_images)
        for phash in sorted([int(x, 16) for x in new_phashes]):
            images = frozenset(itertools.chain.from_iterable([
                phash_images[match]
                for _, match in tree.find(phash, MAX_DISTANCE_IDENTICAL)
            ]))
            if len(images) > 1:
                matched_images.add(images)

        if matched_images:
            for images in sorted(matched_images):
                logger.warning(
                    "Identical: %s",
                    Command.args2cmd(sorted(images)),
                )
            raise SystemExit(1)

    @staticmethod
    def _write(path: Path, image_phashes: dict) -> None:
        logger.info("Writing checksum file: %s", path)

        path_new = Path(f'{path}.part')
        try:
            with pyzstd.open(path_new, 'wt') as ofile:
                for key, phash in image_phashes.items():
                    file, file_size, file_time = key
                    print(
                        f"{phash}/"
                        f"{file_size:010d}/"
                        f"{file_time}  "
                        f"{file}",
                        file=ofile,
                    )
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot create checksum file: {path_new}"
            ) from exception
        try:
            path_new.replace(path)
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot create checksum file: {path}",
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        image_phashes = {}

        update_file = options.get_update_file()
        if update_file:
            image_phashes = self._read(Path(update_file))
        old_keys = set(image_phashes)

        image_phashes = self._update(
             image_phashes,
             options.get_recursive_flag(),
             [Path(x) for x in options.get_files()],
        )

        new_keys = set(image_phashes) - old_keys
        new_phashes = {image_phashes[x] for x in new_keys}
        self._check(image_phashes, new_phashes)
        if new_keys:
            self._write(Path(update_file), image_phashes)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
