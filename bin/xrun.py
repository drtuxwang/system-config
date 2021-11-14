#!/usr/bin/env python3
"""
Run command in new terminal session
"""

import argparse
import glob
import os
import random
import re
import signal
import sys
from typing import List

import command_mod
import subtask_mod

TEXT_FONT = '*-fixed-bold-*-18-*-iso10646-*'
FG_COLOUR = '#009900'
BG_COLOUR = '#000000'
SLEEP = '10'
URI = ('http://', 'https://', 'ftp://')


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_xterm(self) -> command_mod.Command:
        """
        Return xterm Command class object.
        """
        return self._xterm

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Run command in a Xterm.",
        )

        parser.add_argument(
            '-split',
            action='store_true',
            dest='split_flag',
            help="Split command into arguments.",
        )
        parser.add_argument(
            'command',
            nargs=1,
            help="Command with optional arguments.",
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _get_wget(url: str) -> List[str]:
        output = os.path.basename(url).split('?', 1)[0]
        if 'pbs.twimg.com/media/' in url:
            if '?format=jpg' in url:
                output += '.jpg'
                url = url.replace('=medium', '=large')
        return ['wget', '-O', output, url]

    @staticmethod
    def _select_urls(args: List[str]) -> List[str]:
        if [x for x in args if 'instagram' in x]:
            # "/e35/p1080x1080" & "/35/\d{4}"
            ispick = re.compile(r'/e\d\d/.?\d\d\d\d.*_n[.]jpg?')
            return [x for x in args if ispick.search(x)]
        return args

    @classmethod
    def _generate_cmd(cls, args: List[str]) -> List[str]:
        if args[0].startswith(URI):
            nargs = []
            for arg in cls._select_urls(args):
                if '.m3u8' in arg:
                    nargs.extend(['mget', arg, ';'])
                elif 'www.instagram.com/p/' in arg:
                    nargs.extend(['pget', arg, ';'])
                elif 'www.youtube.com/watch?' in arg:
                    nargs.extend(['vget', arg, ';'])
                else:
                    nargs.extend(cls._get_wget(arg) + [';'])
            nargs.extend(['sleep', SLEEP])
        elif len(args) == 2 and args[1].startswith(URI):
            if '.m3u8' in args[1]:
                nargs = ['mget', '-O'] + args + [';', 'sleep', SLEEP]
            elif 'www.youtube.com/watch?' in args[1]:
                nargs = ['vget', '-O'] + args + [';', 'sleep', SLEEP]
            else:
                nargs = ['wget', '-O'] + args + [';', 'sleep', SLEEP]
        else:
            nargs = args + [';', 'sleep', SLEEP]

        return nargs

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if len(args) == 1:
            self._parse_args(args[1:])
        if args[1] == "-split":
            if len(args) != 3:
                self._parse_args(args[1:])
            cmdline = args[2]
            if '"' not in cmdline:
                cmdline = cmdline.replace("'", '"').replace('\n', ' ')
            args[1:] = command_mod.Command.cmd2args(cmdline)

        command = command_mod.Command.args2cmd(self._generate_cmd(args[1:]))
        self._xterm = command_mod.Command('xterm', errors='stop')
        self._xterm.set_args([
            '-fn',
            TEXT_FONT,
            '-fg',
            FG_COLOUR,
            '-bg',
            BG_COLOUR,
            '-cr',
            '#ff0000',
            '-ut',
            '-geometry',
            '100x10+'
            f'{random.randint(20, int(40)):d}+{random.randint(20, int(40)):d}',
            '-T',
            f'xrun: {command}',
            '-e',
            command
        ])


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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        xterm = options.get_xterm()
        subtask_mod.Background(xterm.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
