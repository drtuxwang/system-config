#!/usr/bin/env python3
"""
Wrapper for TMUX terminal multiplexer
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

    def get_tmux(self):
        """
        Return tmux Command class object.
        """
        return self._tmux

    def _select(self):
        self._tmux.set_args(['list-sessions'])
        task = subtask_mod.Batch(self._tmux.get_cmdline())
        task.run(pattern=r'\(created')
        sessions = []
        print("\nTMUX terminal multiplexer")
        for line in task.get_output():
            session = line.split(':')[0]
            info = line.split('windows ', 1)[1]
            print("  Session [{0:s}] {1:s}".format(session, info))
            sessions.append(session)

        selection = input("\nPlease select session name or blank for new: ")
        if selection in sessions:
            self._tmux.set_args(['attach', '-d', '-t', selection])
        elif selection:
            self._tmux.set_args(['new-session', '-s', selection])
        else:
            self._tmux.set_args(['new-session'])

    def parse(self, args):
        """
        Parse arguments
        """
        self._tmux = command_mod.Command('tmux', errors='stop')

        if len(args) > 1:
            self._tmux.set_args(args[1:])
            subtask_mod.Exec(self._tmux.get_cmdline()).run()
        elif os.environ.get('TERM') == 'screen':
            raise SystemExit(
                'sessions should be nested with care, '
                'already running multiplexer')

        self._select()


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

        subtask_mod.Exec(options.get_tmux().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
