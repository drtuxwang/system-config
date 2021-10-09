#!/usr/bin/env python3
"""
Wrapper for "teams" command

Use '-reset' to wipe profile (solves some problems)
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod


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

        file = os.path.join(
            os.environ['HOME'],
            '.config',
            'autostart',
            'teams.desktop',
        )
        if not os.path.isdir(file):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                os.makedirs(file)
            except OSError:
                pass

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        if '-reset' in sys.argv:
            home = os.environ['HOME']
            for directory in glob.glob(
                os.path.join(home, '.config', 'Microsoft*'),
            ):
                if os.path.isdir(directory):
                    print('Removing "{0:s}"...'.format(directory))
                    shutil.rmtree(directory)
            return 0

        teams = command_mod.Command('teams', errors='stop')
        teams.set_args(sys.argv[1:])
        subtask_mod.Exec(teams.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
