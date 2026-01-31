#!/usr/bin/env python3
"""
Show image files with same phash finger print.
"""

import argparse
import itertools
import logging
import os
import signal
import sys
from pathlib import Path
from typing import List

# pylint: disable=import-error
import cv2  # type: ignore
import pybktree  # type: ignore

from command_mod import Command
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

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Show image files with same finger print.",
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
            help="Video file or directory containing image files to compare",
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
        video_phash = {}
        hasher = cv2.img_hash.PHash_create()

        for path in paths:
            if path.is_dir():
                if options.get_recursive_flag() and not path.is_symlink():
                    try:
                        video_phash.update(self._calc(
                            options, list(path.iterdir())
                        ))
                    except PermissionError:
                        pass
            elif path.is_file():
                video = cv2.VideoCapture(path)
                total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(video.get(cv2.CAP_PROP_FPS))
                if total_frames > 2:
                    hashs = []
                    for f in range(fps, min(total_frames, 8*fps+1), fps):
                        video.set(cv2.CAP_PROP_POS_FRAMES, f)
                        _, image = video.read()
                        hashs.append(hasher.compute(image).tobytes().hex())
                    video_phash[path] = ','.join(hashs)

        return video_phash

    @staticmethod
    def _match(phashes: dict) -> set:
        """
        Using BKTree to speed up check:
        if phash1 - phash2 <= MAX_DISTANCE_IDENTICAL:
        """
        phash_videos: dict = {}
        for key, value in phashes.items():
            for v in value.split(','):
                phash = int(v, 16)
                if phash in phash_videos:
                    phash_videos[phash].append(key)
                else:
                    phash_videos[phash] = [key]

        matched_videos: set = set()
        tree = pybktree.BKTree(pybktree.hamming_distance, phash_videos)
        for phash in phash_videos:
            videos = frozenset(itertools.chain.from_iterable([
                phash_videos[match]
                for _, match in tree.find(phash, MAX_DISTANCE_IDENTICAL)
            ]))
            if len(videos) > 1:
                matched_videos.add(videos)

        return matched_videos

    def run(self) -> bool:
        """
        Start program
        """
        options = Options()

        phashes = self._calc(options, [
            Path(x) for x in options.get_files()]
        )
        matched_images = [sorted(x) for x in self._match(phashes)]

        for images in sorted(matched_images):
            logger.warning("Identical: %s", Command.args2cmd(sorted(images)))
        return bool(matched_images)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
