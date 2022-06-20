#!/usr/bin/env python3
"""
Zhong Hua Speak Chinese TTS software.

2009-2021 By Dr Colin Kong
"""

import argparse
import glob
import json
import os
import re
import signal
import sys
import time
from typing import Generator, List

import command_mod
import file_mod
import subtask_mod
import task_mod

RELEASE = '6.0.3'


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release = RELEASE
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_dialect(self) -> str:
        """
        Return dialect.
        """
        return self._args.dialect

    def get_language(self) -> 'Language':
        """
        Return language Command class object
        """
        return self._language

    def get_phrases(self) -> List[str]:
        """
        Return phrases
        """
        return self._phrases

    def get_pinyin_flag(self) -> bool:
        """
        Return Pinyin flag.
        """
        return self._args.pinyin

    def get_speak_dir(self) -> str:
        """
        Return speak directory
        """
        return self._speak_dir

    def get_tmpfile(self) -> str:
        """
        Return tmpfile.
        """
        return self._tmpfile

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"Zhong Hua Speak "
            f"v{self._release} - Chinese TTS software.",
        )

        parser.add_argument(
            '-xclip',
            action='store_true',
            dest='xclip_flag',
            help="Select text from clipboard (enables single session).",
        )
        parser.add_argument(
            '-pinyin',
            action='store_true',
            dest='pinyin',
            help="Print 拼音(Pinyin) or 粵拼(Jyutping) tones only.",
        )
        parser.add_argument(
            '-g',
            action='store_true',
            dest='gui_flag',
            help="Start GUI (zhspeak.tcl).",
        )
        parser.add_argument(
            '-de',
            action='store_const',
            const='de-DE',
            dest='dialect',
            default='zh',
            help="Select Deutsch (德語, German) language.",
        )
        parser.add_argument(
            '-en',
            action='store_const',
            const='en-GB',
            dest='dialect',
            default='zh',
            help="Select English (英語) language.",
        )
        parser.add_argument(
            '-es',
            action='store_const',
            const='es-ES',
            dest='dialect',
            default='zh',
            help="Select Espanol (西班牙語, Spanish) language.",
        )
        parser.add_argument(
            '-fr',
            action='store_const',
            const='fr-FR',
            dest='dialect',
            default='zh',
            help="Select Francese (法語, French) language.",
        )
        parser.add_argument(
            '-it',
            action='store_const',
            const='it-IT',
            dest='dialect',
            default='zh',
            help="Select Italiana (意大利語, Italian) language.",
        )
        parser.add_argument(
            '-zh',
            action='store_const',
            const='zh',
            dest='dialect',
            default='zh',
            help="Select Zhonghua (普通話, Putonghua) dialect (default).",
        )
        parser.add_argument(
            '-zhy',
            action='store_const',
            const='zhy',
            dest='dialect',
            default='zh',
            help="Select Zhonghua Yue (粵語, Cantonese) dialect.",
        )
        parser.add_argument(
            'phrases',
            nargs='*',
            metavar='phrase',
            help="Phrases.",
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _xclip() -> List[str]:
        isxclip = re.compile(os.sep + 'python.*[/ ]zhspeak(.py)? .*-xclip')
        tasks = task_mod.Tasks.factory()
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
                f'{sys.argv[0]}: Error code {task.get_exitcode()} received '
                f'from "{task.get_file()}".',
            )
        return task.get_output()

    def parse(self, args: List[str]) -> None:
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
                    f'{sys.argv[0]}: Cannot find "zhspeak-data" directory.',
                )
            subtask_mod.Exec(zhspeak.get_cmdline()).run()

        if self._args.gui_flag:
            zhspeaktcl = command_mod.Command('zhspeak.tcl', errors='stop')
            subtask_mod.Exec(zhspeaktcl.get_cmdline()).run()

        tmpdir = file_mod.FileUtil.tmpdir('.cache/zhspeak')
        self._tmpfile = os.path.join(tmpdir, f'{os.getpid()}.wav')

        if self._args.xclip_flag:
            self._tmpfile = os.path.join(tmpdir, 'xclip.wav')
            self._phrases = self._xclip()
        else:
            self._phrases = self._args.phrases

        self._language = Language.factory(self)


class Language:
    """
    Language base class
    """

    def __init__(self, _: Options) -> None:
        self._is_found = False

    @staticmethod
    def factory(options: Options) -> 'Language':
        """
        Return Language sub class object
        """
        if options.get_dialect() in ('zh', 'zhy'):
            return Chinese(options)
        for software in (LibttsPico, Espeak):
            tts = software(options)
            if tts.is_found():
                return tts

        raise SystemExit(
            f'{sys.argv[0]}: Cannot find "pico2wave" or "espeak" TTS software.'
        )

    def is_found(self) -> bool:
        """
        Return True if TTS software found.
        """
        return self._is_found

    def text2speech(self, text: List[str]) -> None:
        """
        Text to speech conversion
        """


class Chinese(Language):
    """
    Chinese class
    """

    def __init__(self, options: Options) -> None:
        super().__init__(options)

        self._options = options
        self._directory = os.path.join(
            options.get_speak_dir(),
            options.get_dialect() + '_dir'
        )
        self._dictionary = ChineseDictionary(self._options)

        self._player = AudioPlayer.factory(self._directory)
        if not self._player:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "vlc", '
                '"ffplay" (libav-tools) or "avplay" (ffmpeg).',
            )
        self._is_found = True

    def _speak(self, sounds: List[str]) -> None:
        files = []
        for sound in sounds:
            if os.path.isfile(os.path.join(self._directory, sound + '.mp3')):
                files.append(sound + '.mp3')
            elif os.path.isfile(os.path.join(self._directory, sound + '.ogg')):
                files.append(sound + '.ogg')
            elif os.path.isfile(os.path.join(self._directory, sound + '.wav')):
                files.append(sound + '.wav')
        if files:
            # Pause after every 100 words if no punctuation marks
            for i in range(0, len(files), 10):
                exitcode = self._player.run(files[i:i + 10])
                if exitcode:
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {exitcode} received '
                        f'from "{self._player.get_player()}".',
                    )
                time.sleep(0.25)

    def text2speech(self, text: List[str]) -> None:
        """
        Text to speech conversion
        """
        for phrase in text:
            for sounds in self._dictionary.map_speech(phrase):
                if not self._options.get_pinyin_flag():
                    self._speak(sounds)
                print(" ".join(sounds))


class ChineseDictionary:
    """
    Chinese dictionary class
    """

    def __init__(self, options: Options) -> None:
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
            with open(file, encoding='utf-8', errors='replace') as ifile:
                self._mappings = json.load(ifile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{file}" dialect file.',
            ) from exception
        self._max_block = max(len(key) for key in self._mappings)

    def create_cache(self) -> None:
        """
        Create JSON cache files
        """
        directory = self._options.get_speak_dir()

        file = os.path.join(directory, 'zh.json')
        print(f'Creating "{file}"...')
        self._mappings = {}
        self.readmap(os.path.join(directory, 'en_list'))
        self.readmap(os.path.join(directory, 'zh_list'))
        self.readmap(os.path.join(directory, 'zh_listx'))
        self.readmap(os.path.join(directory, 'zh_listck'))
        try:
            with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                print(
                    json.dumps(self._mappings, ensure_ascii=False),
                    file=ofile,
                )
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{file}" file.',
            ) from exception

        file = os.path.join(directory, 'zhy.json')
        print(f'Creating "{file}"...')
        self._mappings = {}
        self.readmap(os.path.join(directory, 'en_list'))
        self.readmap(os.path.join(directory, 'zhy_list'))
        self.readmap(os.path.join(directory, 'zhy_listck'))
        try:
            with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                print(
                    json.dumps(self._mappings, ensure_ascii=False),
                    file=ofile,
                )
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "{file}" file.',
            ) from exception

    def readmap(self, file: str) -> None:
        """
        Read map
        """
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                for line in ifile.readlines():
                    if line.startswith(('//', '$')):
                        continue
                    if '\t' in line:
                        text, sounds = self._isjunk.sub(
                            '', line).split('\t')[:2]
                        self._mappings[text] = []
                        for match in self._issound.finditer(sounds):
                            self._mappings[text].append(match.group())
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{file}" dialect file.',
            ) from exception

    def map_speech(self, text: str) -> Generator[List[str], None, None]:
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


class LibttsPico(Language):
    """
    LibttsPico class
    """

    def __init__(self, options: Options) -> None:
        super().__init__(options)

        self._tmpfile = options.get_tmpfile()
        self._command = command_mod.Command('pico2wave', errors='ignore')
        self._command.set_args([
            f'--lang={options.get_dialect()}',
            f'--wave={self._tmpfile}'
        ])
        self._is_found = self._command.is_found()

    @staticmethod
    def _speak_sounds(
        cmdline: List[str],
        text: List[str],
        tmpfile: str,
    ) -> None:
        player = AudioPlayer.factory(None)
        if not player:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "vlc", '
                '"ffplay" (libav-tools) or "avplay" (ffmpeg).'
            )

        # Break at '.' and ','
        for phrase in re.sub(r'[^\s\w-]', '.', '.'.join(text)).split('.'):
            if phrase.strip():
                task = subtask_mod.Batch(cmdline + [phrase])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )
                player.run([tmpfile])

        os.remove(tmpfile)

    def text2speech(self, text: List[str]) -> None:
        """
        Text to speech conversion
        """
        cmdline = self._command.get_cmdline()
        self._speak_sounds(cmdline, text, self._tmpfile)


class Espeak(Language):
    """
    Espeak class
    """

    def __init__(self, options: Options) -> None:
        super().__init__(options)

        self._options = options
        self._command = command_mod.Command('espeak-ng', errors='ignore')
        self._command.set_args([
            '-a256',
            '-k30',
            f"-v{options.get_dialect().split('-')[0]}+f2",
            '-s120'
        ])
        self._is_found = self._command.is_found()

    @staticmethod
    def _show_sounds(cmdline: List[str], text: List[str]) -> None:
        task = subtask_mod.Task(cmdline + ['-x', '-q', ' '.join(text)])
        task.run(pattern=': Connection refused')
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
            )

    @staticmethod
    def _speak_sounds(cmdline: List[str], text: List[str]) -> None:
        # Break at '.' and ','
        for phrase in re.sub(r'[^\s\w-]', '.', '.'.join(text)).split('.'):
            if phrase:
                task = subtask_mod.Batch(cmdline + [phrase])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                        f'received from "{task.get_file()}".',
                    )

    def text2speech(self, text: List[str]) -> None:
        """
        Text to speech conversion
        """
        cmdline = self._command.get_cmdline()
        self._show_sounds(cmdline, text)
        self._speak_sounds(cmdline, text)


class AudioPlayer:
    """
    Audio player base class
    """

    def __init__(self, voice_dir: str) -> None:
        self._directory = voice_dir
        self._config()

    @staticmethod
    def factory(directory: str) -> 'AudioPlayer':
        """
        Return AudioPlayer sub class object
        """
        for audio_player in (Vlc, Avplay, Ffplay):
            player = audio_player(directory)
            if player.has_player():
                return player
        return None

    def _config(self) -> None:
        self._player: command_mod.Command = None

    def has_player(self) -> bool:
        """
        Return True if player found
        """
        return self._player.is_found()

    def get_player(self) -> str:
        """
        Return player file location
        """
        return self._player.get_file()

    def run(self, files: List[str]) -> int:
        """
        Run player
        """
        cmdline = self._player.get_cmdline() + files
        task = subtask_mod.Batch(cmdline)
        task.run(directory=self._directory)
        return task.get_exitcode()


class Vlc(AudioPlayer):
    """
    Uses vlc in command-line mode.
    """

    def _config(self) -> None:
        self._player = command_mod.Command('vlc', errors='ignore')
        self._player.set_args([
            '--intf',
            'dummy',
            '--quiet',
            '--no-repeat',
            '--no-loop',
            '--play-and-exit'
        ])


class Ffplay(AudioPlayer):
    """
    Uses 'ffplay' from 'ffmpeg'.
    """

    def _config(self) -> None:
        self._player = command_mod.Command('ffplay', errors='ignore')
        self._player.set_args(['-nodisp', '-autoexit', '-i'])

    def run(self, files: List[str]) -> int:
        """
        Run player
        """
        cmdline = self._player.get_cmdline() + [f"concat:{'|'.join(files)}"]
        task = subtask_mod.Batch(cmdline)
        task.run(directory=self._directory)
        return task.get_exitcode()


class Avplay(Ffplay):
    """
    Uses 'avplay' from 'libav-tools'.
    """

    def _config(self) -> None:
        self._player: command_mod.Command = command_mod.Command(
            'ffplay',
            errors='ignore',
        )
        self._player.set_args(['-nodisp', '-autoexit', '-i'])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    @staticmethod
    def config() -> None:
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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        try:
            options.get_language().text2speech(options.get_phrases())
        except subtask_mod.ExecutableCallError as exception:
            raise SystemExit(exception) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
