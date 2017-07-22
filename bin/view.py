#!/usr/bin/env python3
"""
Viewfiles using default application (uses "view.json").
"""

import argparse
import glob
import json
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

XDESKTOP = {'command': ['xesktop'], 'daemon': False}
URL_PREFIXS = ('http', 'https', 'ftp')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Open files using default application.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to open.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
    def _get_program(command):
        file = os.path.join(os.path.dirname(sys.argv[0]), command[0])
        if os.path.isfile(file):
            return command_mod.CommandFile(file)
        return command_mod.Command(command[0], errors='stop')

    @classmethod
    def _spawn(cls, action, file):
        command = action.get('command')
        if not command:
            raise SystemExit(sys.argv[0] + ': cannot find action: ' + file)
        print(file + ': opening with "' + command[0] + '"...')
        program = cls._get_program(command)
        program.set_args(command[1:] + [file])
        if action.get('daemon'):
            subtask_mod.Daemon(program.get_cmdline()).run()
        else:
            subtask_mod.Task(program.get_cmdline()).run()

    def run(self):
        """
        Start program
        """
        options = Options()
        file = os.path.join(os.path.dirname(sys.argv[0]), 'view.json')
        with open(file) as ifile:
            mappings = json.load(ifile)

        for file in options.get_files():
            if os.path.isdir(file):
                action = XDESKTOP
            elif file.split(':', 1)[0] in URL_PREFIXS:
                action = mappings.get('html')
            elif not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': cannot find file: ' + file)
            else:
                action = mappings.get(
                    '.'.join(file.rsplit('.', 2)[-2:]).lower()
                )
                if not action:
                    action = mappings.get(file.rsplit('.', 1)[-1].lower())
                    if not action:
                        view = command_mod.Command('view', errors='stop')
                        view.set_args([file])
                        subtask_mod.Task(view.get_cmdline()).run()
                        continue
            self._spawn(action, file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
