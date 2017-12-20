#!/usr/bin/env python3
"""
Normalize volume of wave files (-16.0dB rms mean volume).
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_ffmpeg(self):
        """
        Return ffmpeg Command class object.
        """
        return self._ffmpeg

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Normalize volume of wave files '
            '(-16.0dB rms mean volume).'
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='View volume only.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.wav',
            help='Audio file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._ffmpeg = command_mod.Command('ffmpeg', errors='stop')


class Main(object):
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

    def _adjust(self, file, volume):
        change = -16 - float(volume)
        file_new = file + '-new'

        self._ffmpeg.set_args([
            '-i',
            file,
            '-af',
            'volume=' + str(change) + 'dB',
            '-y',
            '-f',
            'wav',
            file_new
        ])
        task = subtask_mod.Batch(self._ffmpeg.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        try:
            shutil.move(file_new, file)
        except OSError:
            os.remove(file_new)
            raise SystemExit(
                sys.argv[0] + ': Cannot update "' + file + '" file.')

    def _view(self, file):
        self._ffmpeg.set_args(
            ['-i', file, "-af", "volumedetect", "-f", "null", "/dev/null"])
        task = subtask_mod.Batch(self._ffmpeg.get_cmdline())
        task.run(pattern=' (mean|max)_volume: .* dB$', error2output=True)
        if len(task.get_output()) != 2:
            raise SystemExit(
                sys.argv[0] + ': Cannot read corrupt "' + file +
                '" wave file.'
            )
        elif task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        volume = task.get_output()[0].split()[-2]
        pvolume = task.get_output()[1].split()[-2]
        return volume, pvolume

    def run(self):
        """
        Start program
        """
        options = Options()

        self._ffmpeg = options.get_ffmpeg()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            elif file[-4:] != '.wav':
                raise SystemExit(
                    sys.argv[0] + ': Cannot handle "' + file +
                    '" non-wave file.'
                )
            volume, pvolume = self._view(file)
            sys.stdout.write(
                file + ": " + volume + " dB (" + pvolume + " dB peak)")
            if not options.get_view_flag():
                for npass in range(4):
                    self._adjust(file, volume)
                    sys.stdout.write(" " + str(npass) + ">> ")
                    volume, pvolume = self._view(file)
                    sys.stdout.write(volume + " dB (" + pvolume + " dB peak)")
                    if volume.startswith('-16.'):
                        break
            print()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
