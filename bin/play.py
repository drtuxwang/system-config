#!/usr/bin/env python3
"""
Play multimedia file/URL.
"""

import argparse
import glob
import logging
import random
import re
import os
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

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_shuffle_flag(self):
        """
        Return shuffle flag.
        """
        return self._args.shuffle_flag

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Play multimedia file/URL.')

        parser.add_argument(
            '-s',
            dest='shuffle_flag',
            action='store_true',
            help='Shuffle order of the media files.'
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='View information.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Multimedia file or URL.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
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
        except IndexError as exception:
            raise SystemExit(
                sys.argv[0] + ': Invalid "' + file + '" media file.'
            ) from exception

    def get_stream(self):
        """
        Generates (stream-number, information) tuples.
        """
        for key, value in sorted(self._stream.items()):
            yield (key, value)

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
        Return True if valid
        """
        return self._type != 'Unknown'

    def show(self):
        """
        Show information
        """
        if self.is_valid():
            logger.info(
                "%s    = Type: %s (%s), %d bytes",
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
    def _view(files):
        for file in files:
            if os.path.isfile(file):
                Media(file).show()

    @staticmethod
    def _play(files):
        vlc = command_mod.Command(
            'vlc',
            args=['--no-repeat', '--no-loop'] + files,
            errors='stop',
        )
        task = subtask_mod.Batch(vlc.get_cmdline())
        task.run(
            pattern="^$|Use 'cvlc'|may be inaccurate|"
            ': Failed to resize display|: call to |: Locale not supported |'
            'fallback "C" locale|^xdg-screensaver:|: cannot estimate delay:|'
            'Failed to open VDPAU backend ')
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )

    def run(self):
        """
        Start program
        """
        options = Options()
        files = options.get_files()

        if options.get_view_flag():
            self._view(files)
        else:
            if options.get_shuffle_flag():
                random.shuffle(files)
            self._play(files)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
