#!/usr/bin/env python3
"""
Speak English words using ZHSpeak TTS engine.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_zhspeak(self):
        """
        Return zhspeak Command class object.
        """
        return self._zhspeak

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Speak words using ZHSpeak TTS engine.'
        )

        parser.add_argument(
            'words',
            nargs='+',
            metavar='word',
            help='A word.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._zhspeak = command_mod.Command(
            'zhspeak',
            args=['-en'] + self._args.words,
            errors='stop',
        )


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
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Task(options.get_zhspeak().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
