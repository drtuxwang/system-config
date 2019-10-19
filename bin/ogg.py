#!/usr/bin/env python3
"""
Encode OGG audio using ffmpeg (libvorbis).
"""

import argparse
import logging
import glob
import os
import re
import signal
import sys

import command_mod
import logging_mod
import subtask_mod

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

    def get_audio_codec(self):
        """
        Return audio codec.
        """
        return self._audio_codec

    def get_audio_quality(self):
        """
        Return audio quality.
        """
        return self._args.audioQuality[0]

    def get_audio_volume(self):
        """
        Return audio volume.
        """
        return self._args.audioVolume[0]

    def get_files(self):
        """
        Return list of files.
        """
        return self._files

    def get_file_new(self):
        """
        Return new file location.
        """
        return self._file_new

    def get_flags(self):
        """
        Return extra flags
        """
        return self._args.flags

    def get_noskip_flag(self):
        """
        Return noskip flag.
        """
        return self._args.noskip_flag

    def get_run_time(self):
        """
        Return run time.
        """
        return self._args.runTime[0]

    def get_start_time(self):
        """
        Return start time.
        """
        return self._args.startTime[0]

    def get_threads(self):
        """
        Return threads.
        """
        return self._args.threads[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Encode OGG audio using ffmpeg (libvorbis).')

        parser.add_argument(
            '-noskip',
            dest='noskip_flag',
            action='store_true',
            help='Disable skipping of encoding when codecs same.'
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
            help='Threads are faster but decrease quality. Default is 2.'
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
            help='Multimedia file. A target ".ogg" file '
            'can be given as the first file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files[0].endswith('.ogg'):
            self._file_new = self._args.files[0]
            self._files = self._args.files[1:]
            if self._file_new in self._args.files[1:]:
                raise SystemExit(
                    sys.argv[0] +
                    ': The input and output files must be different.'
                )
        else:
            self._file_new = ''
            self._files = self._args.files

        self._audio_codec = 'libvorbis'


class Encoder:
    """
    Encoder class
    """

    def __init__(self, options):
        self.config(options)

    def _config_audio(self, media):
        if media.has_audio:
            changing = (
                self._options.get_audio_quality() or
                self._options.get_audio_volume()
            )
            if (not media.has_audio_codec('flac') or
                    self._options.get_noskip_flag() or
                    changing or
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

    def _config(self, file):
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

    def _run(self):
        child = subtask_mod.Child(
            self._ffmpeg.get_cmdline()).run(error2output=True)
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

    def _single(self):
        self._config(self._options.get_files()[0])
        if len(self._options.get_files()) > 1:
            args = []
            maps = ''
            number = 0
            for file in self._options.get_files():
                media = Media(file)
                args.extend(['-i', file])
                for stream, _ in media.get_stream():
                    maps += '[' + str(number) + ':' + str(stream) + ']'
                number += 1
            self._ffmpeg.set_args(args + [
                '-filter_complex',
                maps + 'concat=n=' + str(number) + ':v=0:a=1 [out]',
                '-map',
                '[out]'
            ] + self._ffmpeg.get_args()[2:])
        self._ffmpeg.extend_args(
            ['-f', 'ogg', '-y', self._options.get_file_new()])
        self._run()
        Media(self._options.get_file_new()).show()

    def _multi(self):
        for file in self._options.get_files():
            if not file.endswith('.ogg'):
                self._config(file)
                file_new = file.rsplit('.', 1)[0] + '.ogg'
                self._ffmpeg.extend_args(['-f', 'ogg', '-y', file_new])
                self._run()
                Media(file_new).show()

    def config(self, options):
        """
        Configure encoder
        """
        self._options = options
        self._ffmpeg = command_mod.Command(
            'ffmpeg', args=options.get_flags(), errors='stop')

    def run(self):
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

    def __init__(self, file):
        self._file = file
        self._length = '0'
        self._stream = {}
        self._type = 'Unknown'
        ffprobe = command_mod.Command('ffprobe', args=[file], errors='stop')
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
        except IndexError:
            raise SystemExit(
                sys.argv[0] + ': Invalid "' + file + '" media file.')

    def get_stream(self):
        """
        Return stream
        """
        for key, value in sorted(self._stream.items()):
            yield (key, value)

    def get_stream_audio(self):
        """
        Return audio stream
        """
        for key, value in sorted(self._stream.items()):
            if value.startswith('Audio: '):
                yield (key, value)

    def get_type(self):
        """
        Return media type
        """
        return self._type

    def has_audio(self):
        """
        Return True if audio found
        """
        for value in self._stream.values():
            if value.startswith('Audio: '):
                return True
        return False

    def has_audio_codec(self, codec):
        """
        Return True if audio codec found
        """
        for value in self._stream.values():
            if value.startswith('Audio: ' + codec):
                return True
        return False

    def has_video(self):
        """
        Return True if video found
        """
        for value in self._stream.values():
            if value.startswith('Video: '):
                return True
        return False

    def has_video_codec(self, codec):
        """
        Return True if video codec found
        """
        for value in self._stream.values():
            if value.startswith('Video: ' + codec):
                return True
        return False

    def is_valid(self):
        """
        Return True if valid media
        """
        return self._type != 'Unknown'

    def show(self):
        """
        Print information
        """
        if self.is_valid():
            logger.info(
                "%s    = Type:  %s (%s), %d bytes",
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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        Encoder(options).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
