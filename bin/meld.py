#!/usr/bin/env python3
"""
Wrapper for "meld" command
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_meld(self):
        """
        Return meld Command class object.
        """
        return self._meld

    def parse(self, args):
        """
        Parse arguments
        """
        self._meld = command_mod.Command('meld', errors='stop')
        self._meld.set_args(args[1:])
        self._pattern = (
            ': GtkWarning: | self.recent_manager =| gtk.main()|'
            'accessibility bus address:'
        )


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
    def run():
        """
        Start program
        """
        options = Options()

        os.environ['PYTHONPATH'] = '/usr/lib/python2.7'
        task = subtask_mod.Task(options.get_meld().get_cmdline())
        task.run(pattern=options.get_pattern())
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
