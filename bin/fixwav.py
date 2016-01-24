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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._ffmpeg = syslib.Command('ffmpeg', check=False)
        if not self._ffmpeg.is_found():
            self._ffmpeg = syslib.Command('ffmpeg')

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_normalize(self):
        """
        Return ffmpeg Command class object.
        """
        return self._ffmpeg

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Normalize volume of wave files (-16.0dB rms mean volume).')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View volume only.')

        parser.add_argument('files', nargs='+', metavar='file.wav', help='Audio file.')

        self._args = parser.parse_args(args)


class Normalize(object):
    """
    Normalize class
    """

    def __init__(self, options):
        self._options = options
        self._ffmpeg = options.get_normalize()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            elif file[-4:] != '.wav':
                raise SystemExit(sys.argv[0] + ': Cannot handle "' + file + '" non-wave file.')
            volume, pvolume = self._view(file)
            sys.stdout.write(file + ': ' + volume + ' dB (' + pvolume + ' dB peak)')
            if not options.get_view_flag():
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
        file_new = file + '-new'

        self._ffmpeg.set_args(
            ['-i', file, '-af', 'volume=' + str(change) + 'dB', '-y', '-f', 'wav', file_new])
        self._ffmpeg.run(mode='batch')
        if self._ffmpeg.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ffmpeg.get_exitcode()) +
                             ' received from "' + self._ffmpeg.get_file() + '".')
        try:
            os.rename(file_new, file)
        except OSError:
            os.remove(file_new)
            raise SystemExit(sys.argv[0] + ': Cannot update "' + file + '" file.')

    def _view(self, file):
        self._ffmpeg.set_args(['-i', file, "-af", "volumedetect", "-f", "null", "/dev/null"])
        self._ffmpeg.run(filter=' (mean|max)_volume: .* dB$', mode='batch', error2output=True)
        if len(self._ffmpeg.get_output()) != 2:
            raise SystemExit(sys.argv[0] + ': Cannot read corrupt "' + file + '" wave file.')
        elif self._ffmpeg.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ffmpeg.get_exitcode()) +
                             ' received from "' + self._ffmpeg.get_file() + '".')
        volume = self._ffmpeg.get_output()[0].split()[-2]
        pvolume = self._ffmpeg.get_output()[1].split()[-2]
        return (volume, pvolume)


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
            Normalize(options)
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
