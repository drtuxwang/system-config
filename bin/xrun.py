#!/usr/bin/env python3
"""
Run sudo command in new terminal session
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

FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'
SLEEP = '10'


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
        if args[1].startswith(('http://', 'https://', 'ftp://')):
            nargs = args[:1]
            for arg in args[1:]:
                if 'www.youtube.com/watch?' in arg:
                    nargs.extend(['vget', arg, ';'])
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
        else:
            nargs = args + [';', 'sleep', SLEEP]
        command = command_mod.Command.args2cmd(nargs[1:])

        self._xterm = command_mod.Command('xterm', errors='stop')
        self._xterm.set_args([
            '-fn',
            '-misc-fixed-bold-r-normal--18-*-iso8859-1',
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
