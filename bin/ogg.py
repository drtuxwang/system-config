#!/usr/bin/env python3
"""
Encode OGG audio using ffmpeg (libvorbis).
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._audioCodec = 'libvorbis'

    def getAudioCodec(self):
        """
        Return audio codec.
        """
        return self._audioCodec

    def getAudioQuality(self):
        """
        Return audio quality.
        """
        return self._args.audioQuality[0]

    def getAudioVolume(self):
        """
        Return audio volume.
        """
        return self._args.audioVolume[0]

    def getFiles(self):
        """
        Return list of files.
        """
        return self._files

    def getFileNew(self):
        """
        Return new file location.
        """
        return self._fileNew

    def getFlags(self):
        """
        Return extra flags
        """
        return self._args.flags

    def getNoskipFlag(self):
        """
        Return noskip flag.
        """
        return self._args.noskipFlag

    def getRunTime(self):
        """
        Return run time.
        """
        return self._args.runTime[0]

    def getStartTime(self):
        """
        Return start time.
        """
        return self._args.startTime[0]

    def getThreads(self):
        """
        Return threads.
        """
        return self._args.threads[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Encode OGG audio using ffmpeg (libvorbis).')

        parser.add_argument('-noskip', dest='noskipFlag', action='store_true',
                            help='Disable skipping of encoding when codecs same.')
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
            help='Multimedia file. A target ".ogg" file can be given as the first file.')

        self._args = parser.parse_args(args)

        if self._args.files[0].endswith('.ogg'):
            self._fileNew = self._args.files[0]
            self._files = self._args.files[1:]
            if self._fileNew in self._args.files[1:]:
                raise SystemExit(sys.argv[0] + ': The input and output files must be different.')
        else:
            self._fileNew = ''
            self._files = self._args.files


class Encoder:

    def __init__(self, options):
        self._options = options
        self._ffmpeg = syslib.Command('ffmpeg', flags=options.getFlags())

    def run(self):
        if self._options.getFileNew():
            print()
            self._config(self._options.getFiles()[0])
            if len(self._options.getFiles()) > 1:
                args = []
                maps = ''
                number = 0
                for file in self._options.getFiles():
                    media = Media(file)
                    args.extend(['-i', file])
                    for stream, information in media.getStream():
                        maps += '[' + str(number) + ':' + str(stream) + ']'
                    number += 1
                self._ffmpeg.setArgs(args + [
                    '-filter_complex', maps + 'concat=n=' + str(number) + ':v=0:a=1 [out]',
                    '-map', '[out]'] + self._ffmpeg.getArgs()[2:])
            self._ffmpeg.extendArgs(['-f', 'ogg', '-y', self._options.getFileNew()])
            self._run()
            Media(self._options.getFileNew()).print()
        else:
            for file in self._options.getFiles():
                if not file.endswith('.ogg'):
                    print()
                    self._config(file)
                    fileNew = file.rsplit('.', 1)[0] + '.ogg'
                    self._ffmpeg.extendArgs(['-f', 'ogg', '-y', fileNew])
                    self._run()
                    Media(fileNew).print()

    def _config(self, file):
        media = Media(file)
        self._ffmpeg.setArgs(['-i', file])
        if media.hasAudio:
            if (not media.hasAudioCodec('flac') or self._options.getAudioQuality() or
                    self._options.getAudioVolume() or self._options.getNoskipFlag() or
                    len(self._options.getFiles()) > 1):
                self._ffmpeg.extendArgs(['-c:a', self._options.getAudioCodec()])
                if self._options.getAudioQuality():
                    self._ffmpeg.extendArgs(['-b:a', self._options.getAudioQuality() + 'K'])
                else:
                    self._ffmpeg.extendArgs(['-b:a', '128K'])
                if self._options.getAudioVolume():
                    self._ffmpeg.extendArgs([
                        '-af', 'volume=' + self._options.getAudioVolume() + 'dB'])
            else:
                self._ffmpeg.extendArgs(['-c:a', 'copy'])
        if self._options.getStartTime():
            self._ffmpeg.extendArgs(['-ss', self._options.getStartTime()])
        if self._options.getRunTime():
            self._ffmpeg.extendArgs(['-t', self._options.getRunTime()])
        self._ffmpeg.extendArgs([
            '-vn', '-threads', self._options.getThreads()] + self._options.getFlags())
        return media

    def _run(self):
        child = self._ffmpeg.run(mode='child', error2output=True)
        line = ''
        ispattern = re.compile('^$| version |^ *(built |configuration:|lib|Metadata:|Duration:|'
                               'compatible_brands:|Stream|concat:|Program|service|lastkeyframe)|'
                               '^(In|Out)put | : |^Press|^Truncating|bitstream (filter|malformed)|'
                               'Buffer queue|buffer underflow|message repeated|^\[|p11-kit:|'
                               '^Codec AVOption threads')
        init = False

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


class Media:

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
            for line in ffprobe.getOutput():
                if line.strip().startswith('Duration:'):
                    self._length = line.replace(',', '').split()[1]
                elif line.strip().startswith('Stream #0'):
                    self._stream[number] = isjunk.sub('', line)
                    number += 1
                elif line.strip().startswith('Input #'):
                    self._type = line.replace(', from', '').split()[2]
        except IndexError:
            raise SystemExit(sys.argv[0] + ': Invalid "' + file + '" media file.')

    def print(self):
        if self.isvalid():
            print(self._file + '    = Type: ', self._type, '(' + self._length + '),',
                  str(syslib.FileStat(self._file).getSize()) + ' bytes')
            for stream, information in self.getStream():
                print(self._file + '[' + str(stream) + '] =', information)

    def isvalid(self):
        return self._type != 'Unknown'

    def getDuration(self):
        return self._duration

    def getStream(self):
        for key, value in sorted(self._stream.items()):
            yield (key, value)

    def getStreamAudio(self):
        for key, value in sorted(self._stream.items()):
            if value.startswith('Audio: '):
                yield (key, value)

    def getType(self):
        return self._type

    def hasAudio(self):
        for value in self._stream.values():
            if value.startswith('Audio: '):
                return True
        return False

    def hasAudioCodec(self, codec):
        for value in self._stream.values():
            if value.startswith('Audio: ' + codec):
                return True
        return False

    def hasVideo(self):
        for value in self._stream.values():
            if value.startswith('Video: '):
                return True
        return False

    def hasVideoCodec(self, codec):
        for value in self._stream.values():
            if value.startswith('Video: ' + codec):
                return True
        return False


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
