#!/usr/bin/env python3
"""
Play multimedia file/URL.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import random
import re
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files


    def getShuffleFlag(self):
        """
        Return shuffle flag.
        """
        return self._args.shuffleFlag


    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Play multimedia file/URL.")

        parser.add_argument("-s", dest="shuffleFlag", action="store_true",
                            help="Shuffle order of the media files.")
        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="View information.")
        parser.add_argument("files", nargs="+", metavar="file",
                            help="Multimedia fiel or URL.")

        self._args = parser.parse_args(args)


class Play(syslib.Dump):


    def __init__(self, options):
        self._options = options


    def run(self):
        files = self._options.getFiles()

        if self._options.getViewFlag():
            self._view(files)
        else:
            if self._options.getShuffleFlag():
                random.shuffle(files)
            self._play(files)


    def _play(self, files):
        vlc = syslib.Command("vlc", args=files)
        vlc.run(mode="background",
                filter="^$|Use 'cvlc'|may be inaccurate|"
                       ": Failed to resize display|: call to |: Locale not supported |"
                       "fallback 'C' locale|^xdg-screensaver:|: cannot estimate delay:|"
                       "Failed to open VDPAU backend ")
        if vlc.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(vlc.getExitcode()) +
                             ' received from "' + vlc.getFile() + '".')


    def _view(self, files):
        for file in files:
            if os.path.isfile(file):
                Media(file).print()


class Media(syslib.Dump):


    def __init__(self, file):
        self._file = file
        self._length = "0"
        self._stream = {}
        self._type = "Unknown"
        avprobe = syslib.Command("avprobe", args=[ file ])
        avprobe.run(mode="batch", error2output=True)
        number = 0

        isjunk = re.compile("^ *Stream #[^ ]*: ")
        try:
            for line in avprobe.getOutput():
                if line.strip().startswith("Duration:"):
                    self._length = line.replace(",", "").split()[1]
                elif line.strip().startswith("Stream #0"):
                    self._stream[number] = isjunk.sub("", line)
                    number += 1
                elif line.strip().startswith("Input #"):
                    self._type = line.replace(", from", "").split()[2]
        except IndexError:
            raise SystemExit(sys.argv[0] + ': Invalid "' + file + '" media file.')


    def getStream(self):
        for key in sorted(self._stream.keys()):
            yield (key, self._stream[key])


    def getType(self):
        return self._type


    def hasAudio(self):
        for key in self._stream.keys():
            if self._stream[key].startswith("Audio: "):
                return True
        return False


    def hasAudioCodec(self, codec):
        for key in self._stream.keys():
            if self._stream[key].startswith("Audio: " + codec):
                return True
        return False


    def hasVideo(self):
        for key in self._stream.keys():
            if self._stream[key].startswith("Video: "):
                return True
        return False


    def hasVideoCodec(self, codec):
        for key in self._stream.keys():
            if self._stream[key].startswith("Video: " + codec):
                return True
        return False


    def isvalid(self):
        return self._type != "Unknown"


    def print(self):
        if self.isvalid():
            print(self._file + "    = Type: ", self._type, "(" + self._length + "),",
                  str(syslib.FileStat(self._file).getSize()) + " bytes")
            for stream, information in self.getStream():
                print(self._file + "[" + str(stream) + "] =", information)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Play(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
