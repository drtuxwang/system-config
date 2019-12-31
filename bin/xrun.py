#!/usr/bin/env python3
"""
Run command in new terminal session
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

TEXT_FONT = '*-fixed-bold-*-18-*-iso10646-*'
FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'
SLEEP = '10'
URI = ('http://', 'https://', 'ftp://')


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_xterm(self):
        """
        Return xterm Command class object.
        """
        return self._xterm

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Run command in a Xterm.')

        parser.add_argument(
            '-split',
            action='store_true',
            dest='split_flag',
            help='Split command into arguments.'
        )
        parser.add_argument(
            'command',
            nargs=1,
            help='Command with optional arguments.'
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _generate_cmd(args):
        if args[0].startswith(URI):
            nargs = []
            for arg in args:
                if 'www.youtube.com/watch?' in arg or '.m3u8' in arg:
                    nargs.extend(['vget', '--no-check-certificate', arg, ';'])
                elif 'www.instagram.com/p/' in arg:
                    nargs.extend(['pget', arg, ';'])
                else:
                    nargs.extend([
                        'wget',
                        '--output-document',
                        os.path.basename(arg).split('?', 1)[0],
                        arg,
                        ';'
                    ])
            nargs.extend(['sleep', SLEEP])
        elif len(args) == 2 and args[1].startswith(URI):
            if 'www.youtube.com/watch?' in args[1] or '.m3u8' in args[1]:
                nargs = ['vget', '--no-check-certificate', '-O']

            else:
                nargs = ['wget', '-O']
            nargs.extend(args + [';', 'sleep', SLEEP])
        else:
            nargs = args + [';', 'sleep', SLEEP]

        return nargs

    def parse(self, args):
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
            '100x10',
            '-T',
            'xrun: ' + command,
            '-e',
            command
        ])


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

        xterm = options.get_xterm()
        subtask_mod.Background(xterm.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
