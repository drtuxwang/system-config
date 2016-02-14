#!/usr/bin/env python3
"""
Zhong Hua Speak Chinese TTS software.

2009-2016 By Dr Colin Kong
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import glob
import os
import re
import signal
import sys
import time

import syslib2 as syslib

RELEASE = '3.0.14'

if sys.version_info < (2, 7) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 2.7, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release = RELEASE
        self._args = None
        self.parse(sys.argv)

    def get_dialect(self):
        """
        Return dialect.
        """
        return self._args.dialect

    def get_language(self):
        """
        Return language Command class object
        """
        return self._language

    def get_phrases(self):
        """
        Return phrases
        """
        return self._phrases

    def get_sound_flag(self):
        """
        Return sound flag.
        """
        return self._args.soundFlag

    def get_speak_dir(self):
        """
        Return speak directory
        """
        return self._speak_dir

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Zhong Hua Speak v' + self._release + ', Chinese TTS software.')

        parser.add_argument('-xclip', action='store_true', dest='xclipFlag',
                            help='Select text from clipboard (enables single session).')
        parser.add_argument('-pinyin', action='store_false', dest='soundFlag',
                            help='Print pinyin tones only.')
        parser.add_argument('-g', action='store_true', dest='guiFlag', help='Start GUI.')
        parser.add_argument('-de', action='store_const', const='de', dest='dialect', default='zh',
                            help='Select Deutsch (German) language.')
        parser.add_argument('-en', action='store_const', const='en', dest='dialect', default='zh',
                            help='Select English language.')
        parser.add_argument('-es', action='store_const', const='es', dest='dialect', default='zh',
                            help='Select Espanol (Spanish) language.')
        parser.add_argument('-fr', action='store_const', const='fr', dest='dialect', default='zh',
                            help='Select French language.')
        parser.add_argument('-it', action='store_const', const='it', dest='dialect', default='zh',
                            help='Select Italian language.')
        parser.add_argument('-ru', action='store_const', const='ru', dest='dialect', default='zh',
                            help='Select Russian language.')
        parser.add_argument('-sr', action='store_const', const='sr', dest='dialect', default='zh',
                            help='Select Serbian language.')
        parser.add_argument('-zh', action='store_const', const='zh', dest='dialect', default='zh',
                            help='Select Zhonghua (Mandarin) dialect (default).')
        parser.add_argument('-zhy', action='store_const', const='zhy', dest='dialect', default='zh',
                            help='Select Zhonghua Yue (Cantonese) dialect.')

        parser.add_argument('phrases', nargs='*', metavar='phrase', help='Phrases.')

        self._args = parser.parse_args(args)

    @staticmethod
    def _xclip():
        isxclip = re.compile(os.sep + 'python.* zhspeak .*-xclip')
        task = syslib.Task()
        for pid in task.get_pids():
            if pid != os.getpid():
                if isxclip.search(task.get_process(pid)['COMMAND']):
                    # Kill old zhspeak clipboard
                    task.killpids([pid] + task.get_descendant_pids(pid))
        xclip = syslib.Command('xclip')
        xclip.set_args(['-out', '-selection', '-c', 'test'])
        xclip.run(mode='batch')
        if xclip.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(xclip.get_exitcode()) +
                             ' received from "' + xclip.get_file() + '".')
        return xclip.get_output()

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._speak_dir = os.path.abspath(os.path.join(
            os.path.dirname(args[0]), os.pardir, 'zhspeak-data'))
        if not os.path.isdir(self._speak_dir):
            zhspeak = syslib.Command('zhspeak', args=args[1:], check=False)
            if not zhspeak.is_found():
                raise SystemExit(sys.argv[0] + ': Cannot find "zhspeak-data" directory.')
            zhspeak.run(mode='exec')

        if self._args.guiFlag:
            zhspeaktcl = syslib.Command('zhspeak.tcl')
            zhspeaktcl.run(mode='exec')

        if self._args.xclipFlag:
            self._phrases = self._xclip()
        else:
            self._phrases = self._args.phrases

        self._language = Language.factory(self)


class Language(object):
    """
    Language base class
    """

    @staticmethod
    def factory(options):
        """
        Return Language sub class object
        """
        if options.get_dialect() in ('zh', 'zhy'):
            return Chinese(options)
        else:
            return Espeak(options)

    def text2speech(self, _):
        """
        Text to speech conversion
        """
        pass


class Chinese(Language):
    """
    Chinese class
    """

    def __init__(self, options):
        self._options = options
        self._ogg_dir = os.path.join(options.get_speak_dir(), options.get_dialect() + '_ogg')
        self._dictionary = ChineseDictionary(self._options)
        for player in (Ogg123, Avplay, Ffplay):
            self._ogg_player = player(self._ogg_dir)
            if self._ogg_player.has_player():
                break
        else:
            raise SystemExit(sys.argv[0] + ': Cannot find "ogg123" (vorbis-tools),'
                             ' "ffplay" (libav-tools) or "avplay" (ffmpeg).')

    def text2speech(self, phrases):
        """
        Text to speech conversion
        """
        for phrase in phrases:
            for sounds in self._dictionary.map_speech(phrase):
                print(' '.join(sounds))
                if self._options.get_sound_flag():
                    files = []
                    for sound in sounds:
                        if os.path.isfile(os.path.join(self._ogg_dir, sound + '.ogg')):
                            files.append(sound + '.ogg')
                    if files:
                        # Pause after every 100 words if no punctuation marks
                        for i in range(0, len(files), 10):
                            exitcode = self._ogg_player.run(files[i:i + 10])
                            if exitcode:
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' + str(exitcode) +
                                    ' received from "' + self._ogg_player.get_player() + '".')
                            time.sleep(0.25)


class ChineseDictionary(object):
    """
    Chinese dictionary class
    """

    def __init__(self, options):
        self._options = options
        self._isjunk = re.compile('[()| ]')
        self._issound = re.compile(r'[A-Z]$|[a-z]+\d+')
        self._mappings = {}
        self._max_block = 0
        self.readmap(os.path.join(options.get_speak_dir(), 'en_list'))
        if options.get_dialect() == 'zhy':
            self.readmap(os.path.join(options.get_speak_dir(), 'zhy_list'))
            self.readmap(os.path.join(options.get_speak_dir(), 'zhy_listck'))
        else:
            self.readmap(os.path.join(options.get_speak_dir(), 'zh_list'))
            self.readmap(os.path.join(options.get_speak_dir(), 'zh_listx'))
            self.readmap(os.path.join(options.get_speak_dir(), 'zh_listck'))

    def readmap(self, file):
        """
        Read map
        """
        try:
            with open(file, 'rb') as ifile:
                for line in ifile.readlines():
                    line = line.decode('utf-8', 'replace')
                    if line.startswith('//') or line.startswith('$'):
                        continue
                    elif '\t' in line:
                        text, sounds = self._isjunk.sub('', line).split('\t')[:2]
                        self._mappings[text] = []
                        for match in self._issound.finditer(sounds):
                            self._mappings[text].append(match.group())
                        self._max_block = max(self._max_block, len(text))
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" dialect file.')

    def map_speech(self, text):
        """
        Map Speech
        """
        i = 0
        sounds = []
        while i < len(text):
            for blocksize in range(self._max_block, 0, -1):
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


class Espeak(Language):
    """
    Espeak class
    """

    def __init__(self, options):
        self._options = options
        self._espeak = syslib.Command('espeak')
        self._espeak.set_flags(['-a256', '-k30', '-v' + options.get_dialect() + '+f2', '-s120'])

    def text2speech(self, text):
        """
        Text to speech conversion
        """
        if not self._options.get_sound_flag():
            self._espeak.set_args([' '.join(text)])
            self._espeak.extend_flags(['-x', '-q'])
            self._espeak.run(filter=': Connection refused')
        else:
            # Break at '.' and ','
            for phrase in re.sub(r'[^\s\w-]', '.', '.'.join(text)).split('.'):
                if phrase:
                    self._espeak.set_args([phrase])
                    self._espeak.run(mode='batch')
        if self._espeak.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._espeak.get_exitcode()) +
                             ' received from "' + self._espeak.get_file() + '".')


class Ogg123:
    """
    Uses 'ogg123' from 'vorbis-tools'.
    """

    def __init__(self, oggdir):
        self._oggdir = oggdir
        self._config()

    def _config(self):
        self._player = syslib.Command('ogg123', check=False)

    def has_player(self):
        """
        Return True if player found
        """
        return self._player.is_found()

    def get_player(self):
        """
        Return player file location
        """
        return self._player.get_file()

    def run(self, files):
        """
        Run player
        """
        self._player.set_args(files)
        self._player.run(directory=self._oggdir, mode='batch')
        return self._player.get_exitcode()


class Avplay(Ogg123):
    """
    Uses 'avplay' from 'libav-tools'.
    """

    def _config(self):
        self._player = syslib.Command('ffplay', check=False)
        self._player.set_flags(['-nodisp', '-autoexit', '-i'])

    def run(self, files):
        """
        Run player
        """
        self._player.set_args(['concat:' + '|'.join(files)])
        self._player.run(directory=self._oggdir, mode='batch', filter='p11-kit:')


class Ffplay(Avplay):
    """
    Uses 'ffplay' from 'ffmpeg'.
    """

    def _config(self):
        self._player = syslib.Command('ffplay', check=False)
        self._player.set_flags(['-nodisp', '-autoexit', '-i'])


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
        sys.exit(0)

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
        if sys.version_info < (3, 0):
            for i in range(len(sys.argv)):
                sys.argv[i] = sys.argv[i].decode('utf-8', 'replace')

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        try:
            options.get_language().text2speech(options.get_phrases())

        except syslib.SyslibError as exception:
            raise SystemExit(exception)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
