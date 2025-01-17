#!/usr/bin/env python3
"""
Play multimedia file/URL.
"""

import argparse
import logging
import random
import re
import os
import signal
import sys
from pathlib import Path
from typing import Generator, List, Tuple

from command_mod import Command
from logging_mod import ColoredFormatter
from subtask_mod import Batch

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

    def get_mode(self) -> str:
        """
        Return mode.
        """
        return self._args.mode

    def get_shuffle_flag(self) -> bool:
        """
        Return shuffle flag.
        """
        return self._args.shuffle_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Play multimedia file/URL.",
        )

        parser.add_argument(
            '-s',
            dest='shuffle_flag',
            action='store_true',
            help="Shuffle order of the media files.",
        )
        parser.add_argument(
            '-audio',
            action='store_const',
            const='audio',
            dest='mode',
            default='full',
            help="Play audio in media files.",
        )
        parser.add_argument(
            '-video',
            action='store_const',
            const='video',
            dest='mode',
            help="Play video in media files.",
        )
        parser.add_argument(
            '-v',
            action='store_const',
            const='view',
            dest='mode',
            default='full',
            help="View information.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="Multimedia file or URL.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        # Fix QT 5 button size scaling bug
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
        os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'


class Media:
    """
    Media class
    """

    def __init__(self, file: str) -> None:
        self._file = file
        self._length = '0'
        self._stream = {}
        self._type = 'Unknown'
        ffprobe = Command('ffprobe', args=[file], errors='stop')
        task = Batch(ffprobe.get_cmdline())
        task.run(error2output=True)
        number = 0

        isjunk = re.compile('^ *Stream #[^ ]*: ')
        try:
            for line in task.get_output():
                if line.strip().startswith('Duration:'):
                    self._length = line.replace(',', '').split()[1]
                elif line.strip().startswith('Stream #0'):
                    self._stream[number] = isjunk.sub('', line)
                    number += 1
                elif line.strip().startswith('Input #'):
                    self._type = line.replace(', from', '').split()[2]
        except IndexError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Invalid "{file}" media file.',
            ) from exception

    def get_stream(self) -> Generator[Tuple[int, str], None, None]:
        """
        Generates (stream-number, information) tuples.
        """
        for key, value in sorted(self._stream.items()):
            yield key, value

    def has_audio(self) -> bool:
        """
        Return True if audio found
        """
        for value in self._stream.values():
            if value.startswith('Audio: '):
                return True
        return False

    def has_audio_codec(self, codec: str) -> bool:
        """
        Return True if audio codec found
        """
        for value in self._stream.values():
            if value.startswith(f'Audio: {codec}'):
                return True
        return False

    def has_video(self) -> bool:
        """
        Return True if video found
        """
        for value in self._stream.values():
            if value.startswith('Video: '):
                return True
        return False

    def has_video_codec(self, codec: str) -> bool:
        """
        Return True if video codec found
        """
        for value in self._stream.values():
            if value.startswith(f'Video: {codec}'):
                return True
        return False

    def is_valid(self) -> bool:
        """
        Return True if valid
        """
        return self._type != 'Unknown'

    def show(self) -> None:
        """
        Show information
        """
        if self.is_valid():
            logger.info(
                "%s    = Type: %s (%s), %d bytes",
                self._file,
                self._type,
                self._length,
                Path(self._file).stat().st_size,
            )
            for stream, information in self.get_stream():
                logger.info("%s[%d] = %s", self._file, stream, information)


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
    def _view(files: List[str]) -> None:
        for file in files:
            if Path(file).is_file():
                Media(file).show()

    @staticmethod
    def _play(mode: str, files: List[str]) -> None:
        vlc = Command('vlc', errors='stop')
        vlc.set_args(['--no-repeat', '--no-loop'] + files)
        if mode == 'audio':
            vlc.append_arg('--novideo')
        elif mode == 'video':
            vlc.append_arg('--noaudio')

        task = Batch(vlc.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
            )

    @staticmethod
    def _ytplay(mode: str, file: str) -> None:
        vlc = Command('vlc', args=['--no-repeat', '--no-loop'], errors='stop')
        if mode == 'audio':
            vlc.append_arg('--novideo')
        elif mode == 'video':
            vlc.append_arg('--noaudio')

        ytdlp = Command('yt-dlp', errors='stop')
        ytdlp.set_args(['--get-url', '--format=best', file])
        task = Batch(ytdlp.get_cmdline() + ['|'] + vlc.get_cmdline() + ['-'])
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
            )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        files = options.get_files()
        mode = options.get_mode()

        if mode == 'view':
            self._view(files)
        else:
            if options.get_shuffle_flag():
                random.shuffle(files)
            if files[0].startswith('https://www.youtube.com/'):
                self._ytplay(mode, files[0])
            else:
                self._play(mode, files)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
