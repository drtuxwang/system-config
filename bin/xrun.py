#!/usr/bin/env python3
"""
Run command in new terminal session
"""

import argparse
import glob
import hashlib
import os
import random
import signal
import sys
from pathlib import Path
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
    def _select_urls(args: List[str]) -> List[str]:
        if [x for x in args if 'cdninstagram.com' in x]:
            return [
                x
                for x in args
                if '?stp=dst-jpg' in x and 'cache_key=' in x
            ]
        return args

    @staticmethod
    def _get_output(url: str) -> str:
        output = Path(url).name.split('?', 1)[0]
        if 'pbs.twimg.com/media/' in url:
            if '?format=jpg' in url:
                output += '.jpg'
                url = url.replace('=medium', '=large')
        elif url.endswith('/'):
            md5 = hashlib.md5()
            md5.update(url.encode())
            directory = Path(url[:-1]).name
            output = (
                f'index-{md5.hexdigest()[:9]}.jpg'
                if 'jpg' in directory
                else f'index-{md5.hexdigest()[:9]}.html'
            )
        return output

    @classmethod
    def _get_args_multiple(cls, args: List[str]) -> List[str]:
        nargs = []
        outputs = []
        for arg in cls._select_urls(args):
            if '.m3u8' in arg:
                nargs.extend(['mget', arg, ';'])
            elif 'www.instagram.com/p/' in arg:
                nargs.extend(['pget', arg, ';'])
            elif 'www.youtube.com/watch?' in arg:
                nargs.extend(['vget', arg, ';'])
            elif 'azvprv.com/' in arg:
                nargs.extend(['vlcget', arg, ';'])
            else:
                output = cls._get_output(arg)
                if not Path(output).is_file():
                    outputs.append(output)
                    nargs.extend(['wget', '-O', output, arg, ';'])
        if outputs:
            nargs.extend(['fls', '-t'] + outputs + [';'])
        nargs.extend(['sleep', SLEEP])
        return nargs

    @classmethod
    def _get_args_single(cls, args: List[str]) -> List[str]:
        output, url = args
        if '.m3u8' in url:
            nargs = ['mget', '-O', output, url, ';', 'sleep', SLEEP]
        elif 'www.youtube.com/watch?' in url:
            nargs = ['vget', '-O', output, url, ';', 'sleep', SLEEP]
        elif 'azvprv.com/' in url:
            nargs = ['vlcget', '-O', output, url, ';', 'sleep', SLEEP]
        else:
            nargs = ['wget', '-O', output, url, ';', 'sleep', SLEEP]
        return nargs

    @classmethod
    def _generate_cmd(cls, args: List[str]) -> List[str]:
        if args[0].startswith(URI):
            nargs = cls._get_args_multiple(args)
        elif len(args) == 2 and args[1].startswith(URI):
            nargs = cls._get_args_single(args)
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
            f'{random.randint(20, 40)}+{random.randint(80, 100)}',
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
            sys.exit(exception)  # type: ignore

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
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
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
