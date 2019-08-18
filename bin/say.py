#!/usr/bin/env python3
"""
Speak words using Espeak TTS engine.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_espeak(self):
        """
        Return espeak Command class object.
        """
        return self._espeak

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Speak words using Espeak TTS engine.')

        parser.add_argument(
            '-voice',
            nargs=1,
            metavar='xx+yy',
            help='Select language voice '
            '(ie en+f2, fr+m3, de+f2, zhy+f2).'
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

        self._espeak = command_mod.Command('espeak-ng', errors='stop')
        self._espeak.set_args(['-a128', '-k30', '-ven+f2', '-s60', '-x'])
        if self._args.voice:
            self._espeak.append_arg('-v' + self._args.voice[0])
        self._espeak.extend_args([' '.join(self._args.words)])

        self._pattern = (
            '^ALSA lib|: Connection refused|^Cannot connect|^jack server')


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

        subtask_mod.Task(options.get_espeak().get_cmdline()).run(
            pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
