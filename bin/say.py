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
import time
from typing import List

import gtts  # type: ignore

import command_mod
import file_mod
import subtask_mod
import task_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_run_flag(self) -> bool:
        """
        Return run flag.
        """
        return self._args.run

    def get_tmpfile(self) -> str:
        """
        Return tmpfile.
        """
        return self._tmpfile

    def get_words(self) -> List[str]:
        """
        Return list of words.
        """
        return self._words

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Speak words using Google TTS engine.',
        )

        parser.add_argument(
            '-run',
            action='store_true',
            dest='run',
            help='Run command and announce on completion.'
        )
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

        if args[0:1] == ['-run']:
            args = [args[0], '--'] + args[1:]
        self._args = parser.parse_args(args)

    @staticmethod
    def _xclip() -> List[str]:
        isxclip = re.compile(os.sep + 'python.*[/ ]say(.py)? .*-xclip')
        tasks = task_mod.Tasks.factory()
        for pid in tasks.get_pids():
            if pid != os.getpid():
                if isxclip.search(tasks.get_process(pid)['COMMAND']):
                    # Kill old say.py instances
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

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        tmpdir = file_mod.FileUtil.tmpdir('.cache/say')
        self._tmpfile = os.path.join(tmpdir, "{0:d}.mp3".format(os.getpid()))

        if self._args.xclip_flag:
            self._tmpfile = os.path.join(tmpdir, 'xclip.mp3')
            self._words = self._xclip()
        else:
            self._words = self._args.words


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
    def speak(options: Options) -> None:
        """
        Speak message.
        """
        args = options.get_words()
        exitcode = 0

        if options.get_run_flag():
            start_time = time.time()
            command: command_mod.Command
            if os.path.isfile(args[0]):
                command = command_mod.CommandFile(args[0])
            else:
                command = command_mod.Command(args[0], errors='ignore')
            if command.is_found():
                command.set_args(args[1:])
                task = subtask_mod.Task(command.get_cmdline())
                task.run()
                exitcode = task.get_exitcode()
                if exitcode:
                    args.append('has failed')
                else:
                    args.append('has completed')
            else:
                args = args[:1] + ['not found']
                exitcode = 1
            elapsed_time = time.time() - start_time
            print("Elapsed time (s): {0:5.3f} ".format(elapsed_time))

        tmpfile = options.get_tmpfile()
        ffplay = command_mod.Command('ffplay', errors='stop')
        ffplay.extend_args(['-nodisp', '-autoexit', tmpfile])

        for phrase in re.sub(r'[^\s\w-]', '.', '.'.join(args)).split('.'):
            if phrase.strip():
                tts = gtts.gTTS(phrase)
                tts.save(tmpfile)
                subtask_mod.Batch(ffplay.get_cmdline()).run()
        try:
            os.remove(tmpfile)
        except FileNotFoundError:
            pass

        raise SystemExit(exitcode)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        cls.speak(options)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
