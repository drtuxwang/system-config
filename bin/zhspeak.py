#!/usr/bin/env python3
"""
Zhong Hua Speak Chinese TTS software.

2009-2015 By Dr Colin Kong
"""

from __future__ import absolute_import, division, print_function, unicode_literals

RELEASE = "3.0.7"

import sys
if sys.version_info < (2, 7) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 2.7, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal
import time

import syslib2 as syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])

        self._speakDir = os.path.abspath(os.path.join(os.path.dirname(args[0]),
                                                      os.pardir, "zhspeak-data"))
        if not os.path.isdir(self._speakDir):
            zhspeak = syslib.Command("zhspeak", args=args[1:], check=False)
            if not zhspeak.isFound():
                raise SystemExit(sys.argv[0] + ': Cannot find "zhspeak-data" directory.')
            zhspeak.run(mode="exec")

        if self._args.guiFlag:
            zhspeaktcl = syslib.Command("zhspeak.tcl")
            zhspeaktcl.run(mode="exec")

        if self._args.xclipFlag:
            self._phrases = self._xclip()
        else:
            self._phrases = self._args.phrases

        if self._args.dialect in ("zh", "zhy"):
            self._language = Chinese(self)
        else:
            self._language = Espeak(self)

    def getDialect(self):
        """
        Return dialect.
        """
        return self._args.dialect

    def getLanguage(self):
        """
        Return language Command class object
        """
        return self._language

    def getPhrases(self):
        """
        Return phrases
        """
        return self._phrases

    def getSoundFlag(self):
        """
        Return sound flag.
        """
        return self._args.soundFlag

    def getSpeakDir(self):
        """
        Return speak directory
        """
        return self._speakDir

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Zhong Hua Speak v" + self._release + ", Chinese TTS software.")

        parser.add_argument("-xclip", action="store_true", dest="xclipFlag",
                            help="Select text from clipboard (enables single session).")
        parser.add_argument("-pinyin", action="store_false", dest="soundFlag",
                            help="Print pinyin tones only.")
        parser.add_argument("-g", action="store_true", dest="guiFlag", help="Start GUI.")
        parser.add_argument("-de", action="store_const", const="de", dest="dialect", default="zh",
                            help="Select Deutsch (German) language.")
        parser.add_argument("-en", action="store_const", const="en", dest="dialect", default="zh",
                            help="Select English language.")
        parser.add_argument("-es", action="store_const", const="es", dest="dialect", default="zh",
                            help="Select Espanol (Spanish) language.")
        parser.add_argument("-fr", action="store_const", const="fr", dest="dialect", default="zh",
                            help="Select French language.")
        parser.add_argument("-it", action="store_const", const="it", dest="dialect", default="zh",
                            help="Select Italian language.")
        parser.add_argument("-ru", action="store_const", const="ru", dest="dialect", default="zh",
                            help="Select Russian language.")
        parser.add_argument("-sr", action="store_const", const="sr", dest="dialect", default="zh",
                            help="Select Serbian language.")
        parser.add_argument("-zh", action="store_const", const="zh", dest="dialect", default="zh",
                            help="Select Zhonghua (Mandarin) dialect (default).")
        parser.add_argument("-zhy", action="store_const", const="zhy", dest="dialect", default="zh",
                            help="Select Zhonghua Yue (Cantonese) dialect.")

        parser.add_argument("phrases", nargs="*", metavar="phrase", help="Phrases.")

        self._args = parser.parse_args(args)

    def _xclip(self):
        isxclip = re.compile(os.sep + "python.* zhspeak .*-xclip")
        task = syslib.Task()
        for pid in task.getPids():
            if pid != os.getpid():
                if isxclip.search(task.getProcess(pid)["COMMAND"]):
                    # Kill old zhspeak clipboard
                    task.killpids([pid] + task.getDescendantPids(pid))
        xclip = syslib.Command("xclip")
        xclip.setArgs(["-out", "-selection", "-c", "test"])
        xclip.run(mode="batch")
        if xclip.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(xclip.getExitcode()) +
                             ' received from "' + xclip.getFile() + '".')
        return xclip.getOutput()


class Chinese(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._oggDir = os.path.join(options.getSpeakDir(), options.getDialect() + "_ogg")
        self._dictionary = ChineseDictionary(self._options)
        for Player in (Ogg123, Avplay, Ffplay):
            self._oggPlayer = Player(self._oggDir)
            if self._oggPlayer.hasPlayer():
                break
        else:
            raise SystemExit(sys.argv[0] + ': Cannot find "ogg123" (vorbis-tools),'
                             ' "ffplay" (libav-tools) or "avplay" (ffmpeg).')

    def text2speech(self, phrases):
        for phrase in phrases:
            for sounds in self._dictionary.mapSpeech(phrase):
                print(" ".join(sounds))
                if self._options.getSoundFlag():
                    files = []
                    for sound in sounds:
                        if os.path.isfile(os.path.join(self._oggDir, sound + ".ogg")):
                            files.append(sound + ".ogg")
                    if files:
                        # Pause after every 100 words if no punctuation marks
                        for i in range(0, len(files), 10):
                            exitcode = self._oggPlayer.run(files[i:i + 10])
                            if exitcode:
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' + str(exitcode) +
                                    ' received from "' + self._oggPlayer.getPlayer() + '".')
                            time.sleep(0.25)


class ChineseDictionary(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._isjunk = re.compile("[()| ]")
        self._issound = re.compile("[A-Z]$|[a-z]+\d+")
        self._mappings = {}
        self._maxBlock = 0
        self._readmap(os.path.join(options.getSpeakDir(), "en_list"))
        if (options.getDialect() == "zhy"):
            self._readmap(os.path.join(options.getSpeakDir(), "zhy_list"))
            self._readmap(os.path.join(options.getSpeakDir(), "zhy_listck"))
        else:
            self._readmap(os.path.join(options.getSpeakDir(), "zh_list"))
            self._readmap(os.path.join(options.getSpeakDir(), "zh_listx"))
            self._readmap(os.path.join(options.getSpeakDir(), "zh_listck"))

    def _readmap(self, file):
        try:
            with open(file, "rb") as ifile:
                for line in ifile.readlines():
                    line = line.decode("utf-8", "replace")
                    if line.startswith("//") or line.startswith("$"):
                        continue
                    elif "\t" in line:
                        text, sounds = self._isjunk.sub("", line).split("\t")[:2]
                        self._mappings[text] = []
                        for match in self._issound.finditer(sounds):
                            self._mappings[text].append(match.group())
                        self._maxBlock = max(self._maxBlock, len(text))
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" dialect file.')

    def mapSpeech(self, text):
        i = 0
        sounds = []
        while i < len(text):
            for blocksize in range(self._maxBlock, 0, -1):
                if text[i:i + blocksize] in self._mappings:
                    sounds.extend(self._mappings[text[i:i + blocksize]])
                    i += blocksize
                    break
            else:
                if sounds:
                    yield sounds  # Break speech for non text like punctuation marks
                    sounds = []
                i += 1
        yield sounds


class Espeak(syslib.Dump):

    def __init__(self, options):
        self._options = options
        self._espeak = syslib.Command("espeak")
        self._espeak.setFlags(["-a256", "-k30", "-v" + options.getDialect() + "+f2", "-s120"])

    def text2speech(self, text):
        if not self._options.getSoundFlag():
            self._espeak.setArgs([" ".join(text)])
            self._espeak.extendFlags(["-x", "-q"])
            self._espeak.run(filter=": Connection refused")
        else:
            # Break at "." and ","
            for phrase in re.sub(r"[^\s\w-]", ".", ".".join(text)).split("."):
                if phrase:
                    self._espeak.setArgs([phrase])
                    self._espeak.run(mode="batch")
        if self._espeak.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._espeak.getExitcode()) +
                             ' received from "' + self._espeak.getFile() + '".')


class Ogg123(syslib.Dump):
    """
    Uses "ogg123" from "vorbis-tools".
    """

    def __init__(self, oggdir):
        self._oggdir = oggdir
        self._player = syslib.Command("ogg123", check=False)

    def run(self, files):
        self._player.setArgs(files)
        self._player.run(directory=self._oggdir, mode="batch")
        return self._player.getExitcode()

    def hasPlayer(self):
        return self._player.isFound()

    def getPlayer(self):
        return self._player.getFile()


class Avplay(Ogg123):
    """
    Uses "ffplay" from "libav-tools".
    """

    def __init__(self, oggdir):
        self._oggdir = oggdir
        self._player = syslib.Command("ffplay", check=False)
        self._player.setFlags(["-nodisp", "-autoexit", "-i"])

    def run(self, files):
        self._player.setArgs(["concat:" + "|".join(files)])
        self._player.run(directory=self._oggdir, mode="batch", filter="p11-kit:")


class Ffplay(Avplay):
    """
    Uses "ffplay" from "ffmpeg".
    """

    def __init__(self, oggdir):
        self._oggdir = oggdir
        self._player = syslib.Command("ffplay", check=False)
        self._player.setFlags(["-nodisp", "-autoexit", "-i"])


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            if sys.version_info < (3, 0):
                self._unicodeArgv()
            options = Options(sys.argv)
            options.getLanguage().text2speech(options.getPhrases())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _unicodeArgv(self):
        for i in range(len(sys.argv)):
            sys.argv[i] = sys.argv[i].decode("utf-8", "replace")

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
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
