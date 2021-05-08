#!/usr/bin/env python3
"""
Encode AVI video using ffmpeg (libxvid/libmp3lame).
"""

# Annotation: Fix Class reference run time NameError
from __future__ import annotations
import argparse
import glob
import logging
import os
import re
import signal
import sys
from typing import Generator, List, Tuple

import command_mod
import config_mod
import logging_mod
import subtask_mod

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
        Return extra flags.
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

    def get_video_codec(self) -> str:
        """
        Return video codec.
        """
        return self._video_codec

    def get_video_crop(self) -> str:
        """
        Return video cropping.
        """
        return self._args.videoCrop[0]

    def get_video_quality(self) -> str:
        """
        Return video quality.
        """
        return self._args.videoQuality[0]

    def get_video_rate(self) -> str:
        """
        Return video rate.
        """
        return self._args.videoRate[0]

    def get_video_size(self) -> str:
        """
        Return video size.
        """
        return self._args.videoSize[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Encode AVI video using ffmpeg (libxvid/libmp3lame).')

        parser.add_argument(
            '-noskip',
            dest='noskip_flag',
            action='store_true',
            help='Disable skipping of encoding when codecs same.'
        )
        parser.add_argument(
            '-vq',
            nargs=1,
            dest='videoQuality',
            default=[None],
            help='Video quality (1=best, 31=worse). Default is 4.'
        )
        parser.add_argument(
            '-vfps',
            nargs=1,
            dest='videoRate',
            default=[None],
            help='Select frames per second.'
        )
        parser.add_argument(
            '-vcrop',
            nargs=1,
            dest='videoCrop',
            default=[None],
            metavar='w:h:x:y',
            help='Crop video to W x H with x, y offset from top left.'
        )
        parser.add_argument(
            '-vsize',
            nargs=1,
            dest='videoSize',
            default=[None],
            metavar='x:y',
            help='Resize video to width:height in pixels.'
        )
        parser.add_argument(
            '-aq',
            nargs=1,
            dest='audioQuality',
            default=[None],
            help='Select audio bitrate in kbps (128kbps default).'
        )
        parser.add_argument(
            '-avol',
            nargs=1,
            dest='audioVolume',
            default=[None],
            help='Select audio volume adjustment in dB (ie "-5", "5").'
        )
        parser.add_argument(
            '-start',
            nargs=1,
            dest='startTime',
            default=[None],
            help='Start encoding at time n seconds.'
        )
        parser.add_argument(
            '-time',
            nargs=1,
            dest='runTime',
            default=[None],
            help='Stop encoding after n seconds.'
        )
        parser.add_argument(
            '-threads',
            nargs=1,
            default=['2'],
            help='Threads are faster but decrease quality. '
            'Default is 2.'
        )
        parser.add_argument(
            '-flags',
            nargs=1,
            default=[],
            help="Supply additional flags to ffmpeg."
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Multimedia file. A target ".avi" file can '
            'be given as the first file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files[0].endswith('.avi'):
            self._file_new = self._args.files[0]
            self._files = self._args.files[1:]
            if self._file_new in self._args.files[1:]:
                raise SystemExit(
                    sys.argv[0] + ': The input and output files must be '
                    'different.'
                )
        else:
            self._file_new = ''
            self._files = self._args.files

        self._audio_codec = 'libmp3lame'
        self._video_codec = 'libxvid'


class Encoder:
    """
    Encoder class
    """

    def __init__(self, options: Options):
        self.config(options)

    def _config_video(self, media: Media) -> None:
        if media.has_video():
            changing = (
                self._options.get_video_crop() or
                self._options.get_video_rate() or
                self._options.get_video_quality() or
                self._options.get_video_size()
            )
            if (not media.has_video_codec('mpeg4') or
                    self._options.get_noskip_flag() or
                    changing or
                    len(self._options.get_files()) > 1):
                self._ffmpeg.extend_args([
                    '-c:v',
                    self._options.get_video_codec(),
                    '-flags',
                    '+mv4+aic',
                    '-mbd',
                    'rd',
                    '-g',
                    '300',
                    '-trellis',
                    '2'
                ])
                if self._options.get_video_quality():
                    self._ffmpeg.extend_args(
                        ['-qscale:v', self._options.get_video_quality()])
                else:
                    self._ffmpeg.extend_args(['-qscale:v', '4'])
                if self._options.get_video_rate():
                    self._ffmpeg.extend_args(
                        ['-r:v', self._options.get_video_rate()])
                if self._options.get_video_crop():
                    self._ffmpeg.extend_args(
                        ['-vf', 'crop=' + self._options.get_video_crop()])
                if self._options.get_video_size():
                    self._ffmpeg.extend_args(
                        ['-vf', 'scale=' + self._options.get_video_size()])
            else:
                self._ffmpeg.extend_args(['-c:v', 'copy'])

    def _config_audio(self, media: Media) -> None:
        if media.has_audio:
            if (not media.has_audio_codec('mp3') or
                    self._options.get_audio_quality() or
                    self._options.get_audio_volume() or
                    self._options.get_noskip_flag() or
                    len(self._options.get_files()) > 1):
                self._ffmpeg.extend_args(
                    ['-c:a', self._options.get_audio_codec()])
                if self._options.get_audio_quality():
                    self._ffmpeg.extend_args(
                        ['-b:a', self._options.get_audio_quality() + 'K'])
                else:
                    self._ffmpeg.extend_args(['-b:a', '128K'])
                if self._options.get_audio_volume():
                    self._ffmpeg.extend_args([
                        '-af',
                        'volume=' + self._options.get_audio_volume() + 'dB'
                    ])
            else:
                self._ffmpeg.extend_args(['-c:a', 'copy'])

    def _config(self, file: str) -> Media:
        media = Media(file)
        self._ffmpeg.set_args(['-i', file])

        self._config_video(media)
        self._config_audio(media)

        if self._options.get_start_time():
            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
        if self._options.get_run_time():
            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
        self._ffmpeg.extend_args([
            '-threads',
            self._options.get_threads()
        ] + self._options.get_flags())
        return media

    def _config_images(self, files: List[str]) -> None:
        convert = command_mod.Command('convert', errors='stop')
        extension = '.tmp' + str(os.getpid()) + '.png'
        frame = 0
        for file in files:
            frame += 1
            tmpfile = 'frame{0:08d}'.format(frame) + extension
            self._tempfiles.append(tmpfile)
            convert.set_args([file, tmpfile])
            task = subtask_mod.Task(convert.get_cmdline())
            task.run()
        if self._options.get_video_rate():
            self._ffmpeg.set_args(['-r', self._options.get_video_rate()])
        else:
            self._ffmpeg.set_args(['-r', '2'])
        self._ffmpeg.extend_args([
            '-i',
            'frame%8d' + extension,
            '-c:v',
            self._options.get_video_codec(),
            '-pix_fmt',
            'yuv420p'
        ])
        if self._options.get_video_crop():
            self._ffmpeg.extend_args(
                ['-vf', 'crop=' + self._options.get_video_crop()])
        if self._options.get_video_size():
            self._ffmpeg.extend_args(
                ['-vf', 'scale=' + self._options.get_video_size()])
        else:
            convert.set_args(['-verbose', tmpfile, '/dev/null'])
            task2 = subtask_mod.Batch(convert.get_cmdline())
            task.run()
            try:
                # Must be multiple of 2 in x and y resolutions
                xsize, ysize = task2.get_output()[0].split()[2].split('x')
                self._ffmpeg.extend_args([
                    '-vf',
                    'scale=' + str(int(int(xsize)/2)*2) + ':' +
                    str(int(int(ysize)/2)*2)
                ])
            except (IndexError, ValueError):
                pass
        if self._options.get_start_time():
            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
        if self._options.get_run_time():
            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
        self._ffmpeg.extend_args(['-threads', '1'] + self._options.get_flags())

    def __del__(self) -> None:
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    def _all_images(files: List[str]) -> bool:
        image_extensions = config_mod.Config().get('image_extensions')

        for file in files:
            if os.path.splitext(file)[1] not in image_extensions:
                return False
        return True

    def _run(self) -> None:
        child = subtask_mod.Child(
            self._ffmpeg.get_cmdline()).run(error2output=True)
        line = ''
        ispattern = re.compile(
            '^$| version |^ *(built |configuration:|lib|Metadata:|Duration:|'
            'compatible_brands:|Stream|concat:|Program|service|lastkeyframe)|'
            '^(In|Out)put | : |^Press|^Truncating|'
            'bitstream (filter|malformed)|Buffer queue|buffer underflow|'
            r'message repeated|^\[|p11-kit:'
        )

        while True:
            byte = child.stdout.read(1)
            line += byte.decode('utf-8', 'replace')
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
        if self._all_images(self._options.get_files()):
            self._config_images(self._options.get_files())
            self._ffmpeg.extend_args(
                ['-f', 'mp4', '-y', self._options.get_file_new()])
            self._run()
        else:
            if len(self._options.get_files()) == 1:
                self._config(self._options.get_files()[0])
            else:
                extension = '.tmp' + str(os.getpid()) + '.ts'
                for file in self._options.get_files():
                    media = self._config(file)
                    if media.has_video():
                        self._ffmpeg.extend_args(
                            ['-bsf:v', 'h264_mp4toannexb'])
                    self._ffmpeg.extend_args(
                        ['-f', 'mpegts', '-y', file + extension])
                    self._tempfiles.append(file + extension)
                    self._run()
                self._ffmpeg.set_args([
                    '-i', 'concat:' + '|'.join(self._tempfiles), '-c', 'copy'])
                if media.has_audio():
                    self._ffmpeg.extend_args(['-bsf:a', 'aac_adtstoasc'])
            if self._options.get_start_time():
                self._ffmpeg.extend_args(
                    ['-ss', self._options.get_start_time()])
            if self._options.get_run_time():
                self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
            self._ffmpeg.extend_args([
                '-metadata',
                'title=',
                '-f',
                'mp4',
                '-y',
                self._options.get_file_new()
            ])
            self._run()
        Media(self._options.get_file_new()).show()

    def _multi(self) -> None:
        for file in self._options.get_files():
            if not file.endswith('.avi'):
                if self._all_images([file]):
                    self._config_images([file])
                else:
                    self._config(file)
                    if self._options.get_start_time():
                        self._ffmpeg.extend_args(
                            ['-ss', self._options.get_start_time()])
                    if self._options.get_run_time():
                        self._ffmpeg.extend_args(
                            ['-t', self._options.get_run_time()])
                file_new = file.rsplit('.', 1)[0] + '.mp4'
                self._ffmpeg.extend_args(['-f', 'mp4', '-y', file_new])
                self._run()
                Media(file_new).show()

    def config(self, options: Options) -> None:
        """
        Configure encoder
        """
        self._options = options
        self._ffmpeg = command_mod.Command(
            'ffmpeg', args=options.get_flags(), errors='stop')
        self._tempfiles: List[str] = []

    def run(self) -> None:
        """
        Run encoder
        """
        if self._options.get_file_new():
            self._single()
        else:
            self._multi()


class Media:
    """
    Media class
    """

    def __init__(self, file: str) -> None:
        self._file = file
        self._length = '0'
        self._stream = {}
        self._type = 'Unknown'
        ffprobe = command_mod.Command(
            'ffprobe', args=[file], errors='stop')
        task = subtask_mod.Batch(ffprobe.get_cmdline())
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
                sys.argv[0] + ': Invalid "' + file + '" media file.'
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
            if value.startswith('Audio: ' + codec):
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
            if value.startswith('Video: ' + codec):
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
                "%s    = Type:  %d (%s), %d bytes",
                self._file,
                self._type,
                self._length,
                os.path.getsize(self._file),
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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
