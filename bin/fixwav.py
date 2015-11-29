#!/usr/bin/env python3
"""
Normalize volume of wave files (-16.0dB rms mean volume).
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._ffmpeg = syslib.Command('ffmpeg', check=False)
        if not self._ffmpeg.isFound():
            self._ffmpeg = syslib.Command('ffmpeg')

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getNormalize(self):
        """
        Return ffmpeg Command class object.
        """
        return self._ffmpeg

    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Normalize volume of wave files (-16.0dB rms mean volume).')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View volume only.')

        parser.add_argument('files', nargs='+', metavar='file.wav', help='Audio file.')

        self._args = parser.parse_args(args)


class Normalize:

    def __init__(self, options):
        self._options = options
        self._ffmpeg = options.getNormalize()

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            elif file[-4:] != '.wav':
                raise SystemExit(sys.argv[0] + ': Cannot handle "' + file + '" non-wave file.')
            volume, pvolume = self._view(file)
            sys.stdout.write(file + ': ' + volume + ' dB (' + pvolume + ' dB peak)')
            if not options.getViewFlag():
                for npass in range(4):
                    self._adjust(file, volume)
                    sys.stdout.write(' ' + str(npass) + '>> ')
                    volume, pvolume = self._view(file)
                    sys.stdout.write(volume + ' dB (' + pvolume + ' dB peak)')
                    if volume.startswith('-16.'):
                        break
            print()

    def _adjust(self, file, volume):
        change = -16 - float(volume)
        fileNew = file + '-new'

        self._ffmpeg.setArgs(
            ['-i', file, '-af', 'volume=' + str(change) + 'dB', '-y', '-f', 'wav', fileNew])
        self._ffmpeg.run(mode='batch')
        if self._ffmpeg.getExitcode():
            syslib.Dump().list('debugX', self._ffmpeg)
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ffmpeg.getExitcode()) +
                             ' received from "' + self._ffmpeg.getFile() + '".')
        try:
            os.rename(fileNew, file)
        except OSError:
            os.remove(fileNew)
            raise SystemExit(sys.argv[0] + ': Cannot update "' + file + '" file.')

    def _view(self, file):
        self._ffmpeg.setArgs(['-i', file, "-af", "volumedetect", "-f", "null", "/dev/null"])
        self._ffmpeg.run(filter=' (mean|max)_volume: .* dB$', mode='batch', error2output=True)
        if (len(self._ffmpeg.getOutput()) != 2):
            raise SystemExit(sys.argv[0] + ': Cannot read corrupt "' + file + '" wave file.')
        elif self._ffmpeg.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ffmpeg.getExitcode()) +
                             ' received from "' + self._ffmpeg.getFile() + '".')
        volume = self._ffmpeg.getOutput()[0].split()[-2]
        pvolume = self._ffmpeg.getOutput()[1].split()[-2]
        return (volume, pvolume)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Normalize(options)
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
