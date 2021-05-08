#!/usr/bin/env python3
"""
Wrapper for TMUX terminal multiplexer
"""

import glob
import os
import re
import signal
import socket
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_tmux(self) -> command_mod.Command:
        """
        Return tmux Command class object.
        """
        return self._tmux

    @staticmethod
    def _next(sessions: List[str]) -> str:
        hostname = socket.gethostname().split('.')[0].lower()
        ishost = re.compile(r'{0:s}-\d+$'.format(hostname))
        numbers = [int(x.split('-')[-1]) for x in sessions if ishost.match(x)]
        numbers.append(-1)

        return "{0:s}-{1}".format(hostname, max(numbers)+1)

    def _select(self) -> None:
        self._tmux.set_args(['list-sessions'])
        task = subtask_mod.Batch(self._tmux.get_cmdline())
        task.run(pattern=r'\(created')
        sessions = []
        print("\nTMUX terminal multiplexer (sessions):")
        for line in task.get_output():
            session = line.split(':')[0]
            info = line.split('windows ', 1)[1]
            print("  {0:10s}  {1:s}".format(session, info))
            sessions.append(session)

        selection = input("\nPlease select session name or blank for new: ")
        if selection:
            for session in sessions:
                if selection in session:
                    self._tmux.set_args(['attach', '-d', '-t', session])
                    return
            self._tmux.set_args(['new-session', '-s', selection])
        else:
            self._tmux.set_args(['new-session', '-s', self._next(sessions)])

    def parse(self, args: List[str]) -> None:
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

        subtask_mod.Exec(options.get_tmux().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
