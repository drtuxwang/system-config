#!/usr/bin/env python3
"""
Google TTS wrapper.
"""

import argparse
import glob
import os
import re
import signal
import sys

import gtts

import command_mod
import file_mod
import subtask_mod
import task_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_phrases(self):
        """
        Return list of phrases.
        """
        return self._phrases

    def get_tmpfile(self):
        """
        Return tmpfile.
        """
        return self._tmpfile

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Speak words using Google TTS engine.')

        parser.add_argument(
            '-xclip',
            action='store_true',
            dest='xclip_flag',
            help='Select text from clipboard (enables single session).'
        )
        parser.add_argument(
            'words',
            nargs='*',
            metavar='word',
            help='A word.'
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _xclip():
        isxclip = re.compile(os.sep + 'python.*[/ ]gtts_(.py)? .*-xclip')
        tasks = task_mod.Tasks.factory()
        for pid in tasks.get_pids():
            if pid != os.getpid():
                if isxclip.search(tasks.get_process(pid)['COMMAND']):
                    # Kill old gtts instances
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

        tmpdir = file_mod.FileUtil.tmpdir('.cache/gtts')
        self._tmpfile = os.path.join(tmpdir, "{0:d}.mp3".format(os.getpid()))

        if self._args.xclip_flag:
            self._tmpfile = os.path.join(tmpdir, 'xclip.mp3')
            text = self._xclip()
        else:
            text = self._args.words
        self._phrases = re.sub(r'[^\s\w-]', '.', '.'.join(text)).split('.')


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
    def speak(options):
        """
        Speak phrases.
        """
        tmpfile = options.get_tmpfile()
        ffplay = command_mod.Command('ffplay', errors='stop')
        ffplay.extend_args(['-nodisp', '-autoexit', tmpfile])

        for phrase in options.get_phrases():
            if phrase.strip():
                tts = gtts.gTTS(phrase)
                tts.save(tmpfile)
                subtask_mod.Batch(ffplay.get_cmdline()).run()

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cls.speak(options)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
