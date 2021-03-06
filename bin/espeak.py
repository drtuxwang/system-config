#!/usr/bin/env python3
"""
Wrapper for "espeak espeak

Example:
  espeak -a128 -k30 -ven+f2 -s60 -x "Hello World"
"""

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

    def __init__(self, args):
        self._espeak = command_mod.Command('espeak-ng', errors='stop')
        self._espeak.set_args(args[1:])
        self._pattern = ': Connection refused'

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
        options = Options(sys.argv)

        task = subtask_mod.Task(options.get_espeak().get_cmdline())
        task.run(pattern=options.get_pattern())

        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
