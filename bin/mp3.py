#!/usr/bin/env python3
"""
Encode MP3 audio using ffmpeg (libmp3lame).
"""

import argparse
import logging
import os
import re
import signal
import sys
from pathlib import Path
from typing import Generator, List, Tuple

from command_mod import Command
from file_mod import FileStat, FileUtil
from logging_mod import ColoredFormatter
from subtask_mod import Batch, Child

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

    def get_audio_codec(self) -> str:
        """
        Return audio codec.
        """
        return self._audio_codec

    def get_audio_quality(self) -> str:
        """
        Return audio quality.
        """
        return self._args.audioQuality[0]

    def get_audio_volume(self) -> str:
        """
        Return audio volume.
        """
        return self._args.audioVolume[0]

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._files

    def get_file_new(self) -> str:
        """
        Return new file location.
        """
        return self._file_new

    def get_flags(self) -> List[str]:
        """
        Return extra flags
        """
        return self._args.flags

    def get_noskip_flag(self) -> bool:
        """
        Return noskip flag.
        """
        return self._args.noskip_flag

    def get_run_time(self) -> str:
        """
        Return run time.
        """
        return self._args.runTime[0]

    def get_start_time(self) -> str:
        """
        Return start time.
        """
        return self._args.startTime[0]

    def get_threads(self) -> str:
        """
        Return threads.
        """
        return self._args.threads[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Encode MP3 audio using ffmpeg (libmp3lame).",
        )

        parser.add_argument(
            '-noskip',
            dest='noskip_flag',
            action='store_true',
            help="Disable skipping of encoding when codecs same.",
        )
        parser.add_argument(
            '-aq',
            nargs=1,
            dest='audioQuality',
            default=[None],
            help="Select audio bitrate in kbps (128 default).",
        )
        parser.add_argument(
            '-avol',
            nargs=1,
            dest='audioVolume',
            default=[None],
            help='Select audio volume adjustment in dB (ie "-5", "5").',
        )
        parser.add_argument(
            '-start',
            nargs=1,
            dest='startTime',
            default=[None],
            help="Start encoding at time n seconds.",
        )
        parser.add_argument(
            '-time',
            nargs=1,
            dest='runTime',
            default=[None],
            help="Stop encoding after n seconds.",
        )
        parser.add_argument(
            '-threads',
            nargs=1,
            default=['2'],
            help="Threads are faster but decrease quality. Default is 2.",
        )
        parser.add_argument(
            '-flags',
            nargs=1,
            default=[],
            help="Supply additional flags to ffmpeg.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Multimedia file. A target ".mp3" file '
            'can be given as the first file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files[0].endswith('.mp3'):
            self._file_new = self._args.files[0]
            self._files = self._args.files[1:]
            if not self._files or self._file_new in self._files:
                raise SystemExit(
                    f"{sys.argv[0]}: The input and output files "
                    "must be different.",
                )
        else:
            self._file_new = ''
            self._files = self._args.files

        self._audio_codec = 'libmp3lame'


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
        Return stream
        """
        for key, value in sorted(self._stream.items()):
            yield (key, value)

    def get_stream_audio(self) -> Generator[Tuple[int, str], None, None]:
        """
        Return audio stream
        """
        for key, value in sorted(self._stream.items()):
            if value.startswith('Audio: '):
                yield (key, value)

    def get_type(self) -> str:
        """
        Return media type
        """
        return self._type

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
        Return True if valid media
        """
        return self._type != 'Unknown'

    def show(self) -> None:
        """
        Show information
        """
        if self.is_valid():
            logger.info(
                "%s    = Type:  %s (%s), %d bytes",
                self._file,
                self._type,
                self._length,
                Path(self._file).stat().st_size,
            )
            for stream, information in self.get_stream():
                logger.info("%s[%d] = %s", self._file, stream, information)


class Encoder:
    """
    Encoder class
    """

    def __init__(self, options: Options) -> None:
        self.config(options)

    def _config_audio(self, media: Media) -> None:
        if media.has_audio:
            changing = (
                self._options.get_audio_quality() or
                self._options.get_audio_volume()
            )
            if (not media.has_audio_codec('mp3') or
                    self._options.get_noskip_flag() or
                    changing or
                    len(self._options.get_files()) > 1):
                self._ffmpeg.extend_args([
                    '-c:a',
                    self._options.get_audio_codec(),
                ])
                if self._options.get_audio_quality():
                    self._ffmpeg.extend_args([
                        '-b:a',
                        f'{self._options.get_audio_quality()}K',
                    ])
                else:
                    self._ffmpeg.extend_args(['-b:a', '128K'])
                if self._options.get_audio_volume():
                    self._ffmpeg.extend_args([
                        '-af',
                        f'volume={self._options.get_audio_volume()}dB'
                    ])
            else:
                self._ffmpeg.extend_args(['-c:a', 'copy'])

    def _config(self, file: str) -> Media:
        media = Media(file)
        self._ffmpeg.set_args(['-i', file])

        self._config_audio(media)

        if self._options.get_start_time():
            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
        if self._options.get_run_time():
            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
        self._ffmpeg.extend_args([
            '-vn',
            '-threads',
            self._options.get_threads()
        ] + self._options.get_flags())
        return media

    def _run(self) -> None:
        child = Child(self._ffmpeg.get_cmdline()).run(error2output=True)
        line = ''
        ispattern = re.compile(
            '^$| version |^ *(built |configuration:|lib|Metadata:|Duration:|'
            'compatible_brands:|Stream|concat:|Program|service|lastkeyframe)|'
            '^(In|Out)put | : |^Press|^Truncating|bitstream (filter|'
            'malformed)|Buffer queue|buffer underflow|message repeated|'
            r'^\[|p11-kit:|^Codec AVOption threads|COMPATIBLE_BRANDS:|'
            'concat ->'
        )

        while True:
            byte = child.stdout.read(1)
            line += byte.decode(errors='replace')
            if not byte:
                break
            if byte in (b'\n', b'\r'):
                if not ispattern.search(line):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                line = ''
            elif byte == b'\r':
                sys.stdout.write(line)
                line = ''

        if not ispattern.search(line):
            logger.info(line)
        exitcode = child.wait()
        if exitcode:
            sys.exit(exitcode)

    def _single(self) -> None:
        output_file = self._options.get_file_new()
        self._config(self._options.get_files()[0])
        if len(self._options.get_files()) > 1:
            args = []
            maps = ''
            number = 0
            for file in self._options.get_files():
                media = Media(file)
                args.extend(['-i', file])
                for stream, _ in media.get_stream_audio():
                    maps += f'[{number}:{stream}] '
                number += 1
            self._ffmpeg.set_args(args + [
                '-filter_complex',
                f'{maps}concat=n={number}:v=0:a=1 [out]',
                '-map',
                '[out]'
            ] + self._ffmpeg.get_args()[2:])
        path_tmp = Path(f'{output_file}.part')
        self._ffmpeg.extend_args(['-f', 'mp3', '-y', path_tmp])
        self._run()
        path_tmp.replace(output_file)
        Media(self._options.get_file_new()).show()

    def _multi(self) -> None:
        for file in self._options.get_files():
            if not file.endswith('.mp3'):
                self._config(file)
                file_new = file.rsplit('.', 1)[0] + '.mp3'
                path_tmp = Path(f'{file_new}.part')
                self._ffmpeg.extend_args(['-f', 'mp3', '-y', path_tmp])
                self._run()
                path_tmp.replace(file_new)
                Media(file_new).show()

    def config(self, options: Options) -> None:
        """
        Configure encoder
        """
        self._options = options
        self._ffmpeg = Command('ffmpeg', errors='stop')
        self._ffmpeg.set_args(options.get_flags())

    def run(self) -> None:
        """
        Run encoder
        """
        if self._options.get_file_new():
            self._single()
        else:
            self._multi()
        newest = FileUtil.newest(self._options.get_files())
        file_time = FileStat(newest).get_time()
        os.utime(self._options.get_file_new(), (file_time, file_time))


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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        Encoder(options).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
