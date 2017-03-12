#!/usr/bin/env python3
"""
Zhong Hua Speak Chinese TTS software.

2009-2017 By Dr Colin Kong
"""

import argparse
import glob
import json
import os
import re
import signal
import sys
import time

import command_mod
import subtask_mod
import task_mod

RELEASE = '4.0.2'

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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
        return self._args.sound_flag

    def get_speak_dir(self):
        """
        Return speak directory
        """
        return self._speak_dir

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Zhong Hua Speak v' + self._release +
            ' Chinese TTS software.'
        )

        parser.add_argument(
            '-xclip',
            action='store_true',
            dest='xclip_flag',
            help='Select text from clipboard (enables single session).'
        )
        parser.add_argument(
            '-pinyin',
            action='store_false',
            dest='sound_flag',
            help='Print pinyin tones only.'
        )
        parser.add_argument(
            '-g',
            action='store_true',
            dest='gui_flag',
            help='Start GUI.'
        )
        parser.add_argument(
            '-de',
            action='store_const',
            const='de',
            dest='dialect',
            default='zh',
            help='Select Deutsch (German) language.'
        )
        parser.add_argument(
            '-en',
            action='store_const',
            const='en',
            dest='dialect',
            default='zh',
            help='Select English language.'
        )
        parser.add_argument(
            '-es',
            action='store_const',
            const='es',
            dest='dialect',
            default='zh',
            help='Select Espanol (Spanish) language.'
        )
        parser.add_argument(
            '-fr',
            action='store_const',
            const='fr',
            dest='dialect',
            default='zh',
            help='Select French language.'
        )
        parser.add_argument(
            '-it',
            action='store_const',
            const='it',
            dest='dialect',
            default='zh',
            help='Select Italian language.'
        )
        parser.add_argument(
            '-ru',
            action='store_const',
            const='ru',
            dest='dialect',
            default='zh',
            help='Select Russian language.'
        )
        parser.add_argument(
            '-sr',
            action='store_const',
            const='sr',
            dest='dialect',
            default='zh',
            help='Select Serbian language.'
        )
        parser.add_argument(
            '-zh',
            action='store_const',
            const='zh',
            dest='dialect',
            default='zh',
            help='Select Zhonghua (Mandarin) dialect (default).'
        )
        parser.add_argument(
            '-zhy',
            action='store_const',
            const='zhy',
            dest='dialect',
            default='zh',
            help='Select Zhonghua Yue (Cantonese) dialect.'
        )
        parser.add_argument(
            'phrases',
            nargs='*',
            metavar='phrase',
            help='Phrases.'
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _xclip():
        isxclip = re.compile(os.sep + 'python.*[/ ]zhspeak(.py)? .*-xclip')
        tasks = task_mod.Tasks.factory()
        for pid in tasks.get_pids():
            if 'zhspeak' in tasks.get_process(pid)['COMMAND']:
                print(pid, tasks.get_process(pid)['COMMAND'])
        for pid in tasks.get_pids():
            if pid != os.getpid():
                if isxclip.search(tasks.get_process(pid)['COMMAND']):
                    # Kill old zhspeak clipboard
                    tasks.killpids([pid] + tasks.get_descendant_pids(pid))
        xclip = command_mod.Command('xclip', errors='stop')
        xclip.set_args(['-out', '-selection', '-c', 'test'])
        task = subtask_mod.Batch(xclip.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        return task.get_output()

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._speak_dir = os.path.abspath(
            os.path.join(os.path.dirname(args[0]), os.pardir, 'zhspeak-data'))
        if not os.path.isdir(self._speak_dir):
            zhspeak = command_mod.Command(
                'zhspeak',
                args=args[1:],
                errors='ignore'
            )
            if not zhspeak.is_found():
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "zhspeak-data" directory.')
            subtask_mod.Exec(zhspeak.get_cmdline()).run()

        if self._args.gui_flag:
            zhspeaktcl = command_mod.Command('zhspeak.tcl', errors='stop')
            subtask_mod.Exec(zhspeaktcl.get_cmdline()).run()

        if self._args.xclip_flag:
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
        self._ogg_dir = os.path.join(
            options.get_speak_dir(),
            options.get_dialect() + '_ogg'
        )
        self._dictionary = ChineseDictionary(self._options)
        for player in (Ogg123, Avplay, Ffplay):
            self._ogg_player = player(self._ogg_dir)
            if self._ogg_player.has_player():
                break
        else:
            raise SystemExit(
                sys.argv[0] + ': Cannot find "ogg123" (vorbis-tools),'
                ' "ffplay" (libav-tools) or "avplay" (ffmpeg).'
            )

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
                        if os.path.isfile(
                                os.path.join(self._ogg_dir, sound + '.ogg')):
                            files.append(sound + '.ogg')
                    if files:
                        # Pause after every 100 words if no punctuation marks
                        for i in range(0, len(files), 10):
                            exitcode = self._ogg_player.run(files[i:i + 10])
                            if exitcode:
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(exitcode) + ' received from "' +
                                    self._ogg_player.get_player() + '".'
                                )
                            time.sleep(0.25)


class ChineseDictionary(object):
    """
    Chinese dictionary class
    """

    def __init__(self, options):
        self._options = options
        self._isjunk = re.compile('[()| ]')
        self._issound = re.compile(r'[A-Z]$|[a-z]+\d+')

        if options.get_dialect() == 'zhy':
            file = os.path.join(options.get_speak_dir(), 'zhy.json')
        else:
            file = os.path.join(options.get_speak_dir(), 'zh.json')
        if not os.path.isfile(file):
            self.create_cache()

        try:
            with open(file) as ifile:
                self._mappings = json.load(ifile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + file + '" dialect file.')
        self._max_block = max([len(key) for key in self._mappings])

    def create_cache(self):
        """
        Create JSON cache files
        """
        directory = self._options.get_speak_dir()

        file = os.path.join(directory, 'zh.json')
        print('Creating "{0:s}"...'.format(file))
        self._mappings = {}
        self.readmap(os.path.join(directory, 'en_list'))
        self.readmap(os.path.join(directory, 'zh_list'))
        self.readmap(os.path.join(directory, 'zh_listx'))
        self.readmap(os.path.join(directory, 'zh_listck'))
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(self._mappings), file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" file.')

        file = os.path.join(directory, 'zhy.json')
        print('Creating "{0:s}"...'.format(file))
        self._mappings = {}
        self.readmap(os.path.join(directory, 'en_list'))
        self.readmap(os.path.join(directory, 'zhy_list'))
        self.readmap(os.path.join(directory, 'zhy_listck'))
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(self._mappings), file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" file.')

    def readmap(self, file):
        """
        Read map
        """
        try:
            with open(file, 'rb') as ifile:
                for line in ifile.readlines():
                    line = line.decode('utf-8', 'replace')
                    if line.startswith(('//', '$')):
                        continue
                    elif '\t' in line:
                        text, sounds = self._isjunk.sub(
                            '', line).split('\t')[:2]
                        self._mappings[text] = []
                        for match in self._issound.finditer(sounds):
                            self._mappings[text].append(match.group())
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + file + '" dialect file.')

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
                    # Break speech for non text like punctuation marks
                    yield sounds
                    sounds = []
                i += 1
        yield sounds


class Espeak(Language):
    """
    Espeak class
    """

    def __init__(self, options):
        self._options = options
        self._espeak = command_mod.Command('espeak', errors='stop')
        self._espeak.set_args(
            ['-a256', '-k30', '-v' + options.get_dialect() + '+f2', '-s120'])

    @staticmethod
    def _show_sounds(cmdline, text):
        task = subtask_mod.Task(cmdline + ['-x', '-q', ' '.join(text)])
        task.run(pattern=': Connection refused')
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )

    @staticmethod
    def _speak_sounds(cmdline, text):
        # Break at '.' and ','
        for phrase in re.sub(r'[^\s\w-]', '.', '.'.join(text)).split('.'):
            if phrase:
                task = subtask_mod.Batch(cmdline + [phrase])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) +
                        ' received from "' + task.get_file() + '".'
                    )

    def text2speech(self, text):
        """
        Text to speech conversion
        """
        cmdline = self._espeak.get_cmdline()
        self._show_sounds(cmdline, text)
        if self._options.get_sound_flag():
            self._speak_sounds(cmdline, text)


class Ogg123:
    """
    Uses 'ogg123' from 'vorbis-tools'.
    """

    def __init__(self, oggdir):
        self._oggdir = oggdir
        self._config()

    def _config(self):
        self._player = command_mod.Command('ogg123', errors='ignore')

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
        cmdline = self._player.get_cmdline() + files
        task = subtask_mod.Batch(cmdline)
        task.run(directory=self._oggdir)
        return task.get_exitcode()


class Ffplay(Ogg123):
    """
    Uses 'ffplay' from 'ffmpeg'.
    """

    def _config(self):
        self._player = command_mod.Command('ffplay', errors='ignore')
        self._player.set_args(['-nodisp', '-autoexit', '-i'])

    def run(self, files):
        """
        Run player
        """
        cmdline = self._player.get_cmdline() + ['concat:' + '|'.join(files)]
        task = subtask_mod.Batch(cmdline)
        task.run(directory=self._oggdir)
        return task.get_exitcode()


class Avplay(Ffplay):
    """
    Uses 'avplay' from 'libav-tools'.
    """

    def _config(self):
        self._player = command_mod.Command('ffplay', errors='ignore')
        self._player.set_args(['-nodisp', '-autoexit', '-i'])


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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        try:
            options.get_language().text2speech(options.get_phrases())
        except subtask_mod.ExecutableCallError as exception:
            raise SystemExit(exception)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
