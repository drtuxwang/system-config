#!/usr/bin/env python3
"""
Calculate checksum lines using phash, file size and file modification time.
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
import cv2  # type: ignore
import pybktree  # type: ignore
import pyzstd  # type: ignore

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
            description="Calculate checksum lines using phash, file size "
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
            metavar='file',
            help='Video file to perceptual hash (phash).',
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
        logger.info("Using checksum file: %s", path)
        phashes: dict = {}
        if not path.is_file():
            return phashes

        logger.info("Reading checksum file...")
        try:
            with pyzstd.open(path, 'rt', errors='replace') as ifile:
                for line in ifile:
                    try:
                        line = line.rstrip('\n')
                        checksum, size, mtime, file = cls._get_checksum(line)
                        if file:
                            phashes[(file, size, mtime)] = checksum
                    except IndexError:
                        pass
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot read checksum file: {path}",
            ) from exception
        return phashes

    @classmethod
    def _update(
        cls,
        phashes: dict,
        recursive: bool,
        paths: List[Path],
    ) -> dict:
        logger.info("Updating checksums...")
        new_phashes = {}
        hasher = cv2.img_hash.PHash_create()

        for path in paths:
            if path.is_dir():
                if recursive and not path.is_symlink():
                    try:
                        new_phashes.update(cls._update(
                            phashes, recursive, list(path.iterdir())
                        ))
                    except PermissionError:
                        pass
            elif path.is_file():
                file_stat = FileStat(path)
                key = (
                     str(path),
                     file_stat.get_size(), int(file_stat.get_mtime()),
                )
                if key in phashes:
                    new_phashes[key] = phashes[key]
                else:
                    video = cv2.VideoCapture(path)
                    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(video.get(cv2.CAP_PROP_FPS))
                    if total_frames > 2:
                        hashs = []
                        for f in range(fps, min(total_frames, 8*fps+1), fps):
                            video.set(cv2.CAP_PROP_POS_FRAMES, f)
                            _, image = video.read()
                            hashs.append(hasher.compute(image).tobytes().hex())
                        new_phashes[key] = ','.join(hashs)

        return new_phashes

    @classmethod
    def _check(cls, phashes: dict, new_phashes: Set[str]) -> None:
        """
        Using BKTree to speed up check:
        if phash1 - phash2 <= MAX_DISTANCE_IDENTICAL:
        """
        logger.info("Checking checksums...")

        phash_videos: dict = {}
        for key, value in phashes.items():
            for v in value.split(','):
                phash = int(v, 16)
                file, _, _ = key
                if phash in phash_videos:
                    phash_videos[phash].append(file)
                else:
                    phash_videos[phash] = [file]

        matched_videos = set()
        tree = pybktree.BKTree(pybktree.hamming_distance, phash_videos)
        for hashes in new_phashes:
            for phash in [int(x, 16) for x in hashes.split(',')]:
                videos = frozenset(itertools.chain.from_iterable([
                    phash_videos[match]
                    for _, match in tree.find(phash, MAX_DISTANCE_IDENTICAL)
                ]))
                if len(videos) > 1:
                    matched_videos.add(videos)
        if matched_videos:
            for videos in sorted(matched_videos):
                logger.warning(
                    "Identical: %s",
                    Command.args2cmd(sorted(videos)),
                )
            raise SystemExit(1)

    @staticmethod
    def _write(path: Path, phashes: dict) -> None:
        logger.info("Writing checksum file...")

        path_new = Path(f'{path}.part')
        try:
            with pyzstd.open(path_new, 'wt') as ofile:
                for key, phash in sorted(phashes.items()):
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

    @staticmethod
    def _show(phashes: dict) -> None:
        for key, phash in sorted(phashes.items()):
            file, file_size, file_time = key
            print(
                f"{phash}/"
                f"{file_size:010d}/"
                f"{file_time}  "
                f"{file}",
            )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        phashes = {}

        update_file = options.get_update_file()
        if update_file:
            phashes = self._read(Path(update_file))
        old_keys = set(phashes)

        phashes = self._update(
             phashes,
             options.get_recursive_flag(),
             [Path(x) for x in options.get_files()],
        )

        new_keys = set(phashes) - old_keys
        new_phashes = {phashes[x] for x in new_keys}
        if not update_file:
            self._show(phashes)
        self._check(phashes, new_phashes)
        if update_file and new_keys:
            self._write(Path(update_file), phashes)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
