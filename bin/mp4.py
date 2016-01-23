#!/usr/bin/env python3
"""
Encode MP4 video using ffmpeg (libx264/aac).
"""

import argparse
import glob
import os
import re
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._audio_codec = 'aac'
        self._video_codec = 'libx264'

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
        return self._args.noskipFlag

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

    def get_video_codec(self):
        """
        Return video codec.
        """
        return self._video_codec

    def get_video_crop(self):
        """
        Return video cropping.
        """
        return self._args.videoCrop[0]

    def get_video_quality(self):
        """
        Return video quality.
        """
        return self._args.videoQuality[0]

    def get_video_rate(self):
        """
        Return video rate.
        """
        return self._args.videoRate[0]

    def get_video_size(self):
        """
        Return video size.
        """
        return self._args.videoSize[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Encode MP4 video using ffmpeg (libx264/aac).')

        parser.add_argument('-noskip', dest='noskipFlag', action='store_true',
                            help='Disable skipping of encoding when codecs same.')
        parser.add_argument('-vq', nargs=1, dest='videoQuality', default=[None],
                            help='x264 quality (0=loseless, 51=worse). Default is 23.')
        parser.add_argument('-vfps', nargs=1, dest='videoRate', default=[None],
                            help='Select frames per second.')
        parser.add_argument('-vcrop', nargs=1, dest='videoCrop', default=[None], metavar='w:h:x:y',
                            help='Crop video to W x H with x, y offset from top left.')
        parser.add_argument('-vsize', nargs=1, dest='videoSize', default=[None], metavar='x:y',
                            help='Resize video to width:height in pixels.')
        parser.add_argument('-aq', nargs=1, dest='audioQuality', default=[None],
                            help='Select audio bitrate in kbps (128kbps default).')
        parser.add_argument('-avol', nargs=1, dest='audioVolume', default=[None],
                            help='Select audio volume adjustment in dB (ie "-5", "5").')
        parser.add_argument('-start', nargs=1, dest='startTime', default=[None],
                            help='Start encoding at time n seconds.')
        parser.add_argument('-time', nargs=1, dest='runTime', default=[None],
                            help='Stop encoding after n seconds.')
        parser.add_argument('-threads', nargs=1, default=['2'],
                            help='Threads are faster but decrease quality. Default is 2.')
        parser.add_argument('-flags', nargs=1, default=[],
                            help="Supply additional flags to ffmpeg.")

        parser.add_argument(
            'files', nargs='+', metavar='file',
            help='Multimedia file. A target ".mp4" file can be given as the first file.')

        self._args = parser.parse_args(args)

        if self._args.files[0].endswith('.mp4'):
            self._file_new = self._args.files[0]
            self._files = self._args.files[1:]
            if self._file_new in self._args.files[1:]:
                raise SystemExit(sys.argv[0] + ': The input and output files must be different.')
        else:
            self._file_new = ''
            self._files = self._args.files


class Encoder(object):
    """
    Encoder class
    """

    def __init__(self, options):
        self._options = options
        self._ffmpeg = syslib.Command('ffmpeg', flags=options.get_flags())
        self._tempfiles = []

    def run(self):
        """
        Run encoder
        """
        if self._options.get_file_new():
            print()
            if self._all_images(self._options.get_files()):
                self._config_images(self._options.get_files())
                self._ffmpeg.extend_args(['-f', 'mp4', '-y', self._options.get_file_new()])
                self._run()
            else:
                if len(self._options.get_files()) == 1:
                    self._config(self._options.get_files()[0])
                else:
                    extension = '-tmpfile' + str(os.getpid()) + '.ts'
                    for file in self._options.get_files():
                        media = self._config(file)
                        if media.has_video():
                            self._ffmpeg.extend_args(['-bsf:v', 'h264_mp4toannexb'])
                        self._ffmpeg.extend_args(['-f', 'mpegts', '-y', file + extension])
                        self._tempfiles.append(file + extension)
                        self._run()
                    self._ffmpeg.set_args([
                        '-i', 'concat:' + '|'.join(self._tempfiles), '-c', 'copy'])
                    if media.has_audio():
                        self._ffmpeg.extend_args(['-bsf:a', 'aac_adtstoasc'])
                if self._options.get_start_time():
                    self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
                if self._options.get_run_time():
                    self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
                self._ffmpeg.extend_args([
                    '-metadata', 'title=', '-f', 'mp4', '-y', self._options.get_file_new()])
                self._run()
            Media(self._options.get_file_new()).print()
        else:
            for file in self._options.get_files():
                if not file.endswith('.mp4'):
                    print()
                    if self._all_images([file]):
                        self._config_images([file])
                    else:
                        self._config(file)
                        if self._options.get_start_time():
                            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
                        if self._options.get_run_time():
                            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
                    file_new = file.rsplit('.', 1)[0] + '.mp4'
                    self._ffmpeg.extend_args(['-f', 'mp4', '-y', file_new])
                    self._run()
                    Media(file_new).print()

    def _config(self, file):
        media = Media(file)
        self._ffmpeg.set_args(['-i', file])

        if media.has_video():
            if (not media.has_video_codec('h264') or self._options.get_video_crop() or
                    self._options.get_video_rate() or self._options.get_video_quality() or
                    self._options.get_video_size() or self._options.get_noskip_flag()):
                self._ffmpeg.extend_args([
                    '-c:v', self._options.get_video_codec(), '-subq', '10', '-trellis', '2'])
                if self._options.get_video_quality():
                    self._ffmpeg.extend_args(['-crf:v', self._options.get_video_quality()])
                else:
                    self._ffmpeg.extend_args(['-crf:v', '23'])
                if self._options.get_video_rate():
                    self._ffmpeg.extend_args(['-r:v', self._options.get_video_rate()])
                if self._options.get_video_crop():
                    self._ffmpeg.extend_args(['-vf', 'crop=' + self._options.get_video_crop()])
                if self._options.get_video_size():
                    self._ffmpeg.extend_args(['-vf', 'scale=' + self._options.get_video_size()])
            else:
                self._ffmpeg.extend_args(['-c:v', 'copy'])

        if media.has_audio:
            if (not media.has_audio_codec('aac') or self._options.get_audio_quality() or
                    self._options.get_audio_volume() or self._options.get_noskip_flag()):
                self._ffmpeg.extend_args(['-c:a', self._options.get_audio_codec()])
                if self._options.get_audio_quality():
                    self._ffmpeg.extend_args(['-b:a', self._options.get_audio_quality() + 'K'])
                else:
                    self._ffmpeg.extend_args(['-b:a', '128K'])
                if self._options.get_audio_volume():
                    self._ffmpeg.extend_args([
                        '-af', 'volume=' + self._options.get_audio_volume() + 'dB'])
                self._ffmpeg.extend_args(['-strict', 'experimental'])  # Required for 'aac' audio
            else:
                self._ffmpeg.extend_args(['-c:a', 'copy'])

        if self._options.get_start_time():
            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
        if self._options.get_run_time():
            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
        self._ffmpeg.extend_args([
            '-threads', self._options.get_threads()] + self._options.get_flags())
        return media

    def _config_images(self, files):
        convert = syslib.Command('convert')
        extension = '-tmpfile' + str(os.getpid()) + '.png'
        frame = 0
        for file in files:
            frame += 1
            tmpfile = 'frame{0:08d}'.format(frame) + extension
            self._tempfiles.append(tmpfile)
            convert.set_args([file, tmpfile])
            convert.run()
        if self._options.get_video_rate():
            self._ffmpeg.set_args(['-r', self._options.get_video_rate()])
        else:
            self._ffmpeg.set_args(['-r', '2'])
        self._ffmpeg.extend_args(['-i', 'frame%8d' + extension, '-c:v',
                                  self._options.get_video_codec(), '-pix_fmt', 'yuv420p'])
        if self._options.get_video_crop():
            self._ffmpeg.extend_args(['-vf', 'crop=' + self._options.get_video_crop()])
        if self._options.get_video_size():
            self._ffmpeg.extend_args(['-vf', 'scale=' + self._options.get_video_size()])
        else:
            convert.set_args(['-verbose', tmpfile, '/dev/null'])
            convert.run(mode='batch')
            try:
                # Must be multiple of 2 in x and y resolutions
                xsize, ysize = convert.get_output()[0].split()[2].split('x')
                self._ffmpeg.extend_args([
                    '-vf', 'scale=' + str(int(int(xsize)/2)*2) + ':' + str(int(int(ysize)/2)*2)])
            except (IndexError, ValueError):
                pass
        if self._options.get_start_time():
            self._ffmpeg.extend_args(['-ss', self._options.get_start_time()])
        if self._options.get_run_time():
            self._ffmpeg.extend_args(['-t', self._options.get_run_time()])
        self._ffmpeg.extend_args(['-threads', '1'] + self._options.get_flags())

    def __del__(self):
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass

    def _all_images(self, files):
        for file in files:
            extension = file.split('.')[-1]
            if extension not in ('bmp', 'gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff'):
                return False
        return True

    def _run(self):
        child = self._ffmpeg.run(mode='child', error2output=True)
        line = ''
        ispattern = re.compile('^$| version |^ *(built |configuration:|lib|Metadata:|Duration:|'
                               'compatible_brands:|Stream|concat:|Program|service|lastkeyframe)|'
                               '^(In|Out)put | : |^Press|^Truncating|bitstream (filter|malformed)|'
                               r'Buffer queue|buffer underflow|message repeated|^\[|p11-kit:')

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
            print(line)
        exitcode = child.wait()
        if exitcode:
            sys.exit(exitcode)


class Media(object):
    """
    Media class
    """

    def __init__(self, file):
        self._file = file
        self._length = '0'
        self._stream = {}
        self._type = 'Unknown'
        ffprobe = syslib.Command('ffprobe', args=[file])
        ffprobe.run(mode='batch', error2output=True)
        number = 0
        isjunk = re.compile('^ *Stream #[^ ]*: ')
        try:
            for line in ffprobe.get_output():
                if line.strip().startswith('Duration:'):
                    self._length = line.replace(',', '').split()[1]
                elif line.strip().startswith('Stream #0'):
                    self._stream[number] = isjunk.sub('', line)
                    number += 1
                elif line.strip().startswith('Input #'):
                    self._type = line.replace(', from', '').split()[2]
        except IndexError:
            raise SystemExit(sys.argv[0] + ': Invalid "' + file + '" media file.')

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

    def print(self):
        """
        Print information
        """
        if self.is_valid():
            print(self._file + '    = Type: ', self._type, '(' + self._length + '),',
                  str(syslib.FileStat(self._file).get_size()) + ' bytes')
            for stream, information in self.get_stream():
                print(self._file + '[' + str(stream) + '] =', information)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Encoder(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
