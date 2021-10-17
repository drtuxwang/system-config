#!/usr/bin/env python3
"""
Wrapper for "teams" command
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import file_mod
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

    @staticmethod
    def _config_teams() -> None:
        home = os.environ['HOME']
        file = os.path.join(home, '.config', 'autostart', 'teams.desktop')
        if not os.path.isdir(file):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                os.makedirs(file)
            except OSError:
                pass

        # Use /tmp cache (keep "Cookies" & "desktop-config.json")
        config_dir = os.path.join(
            home,
            '.config',
            'Microsoft',
            'Microsoft Teams Config',
        )
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        tmpdir = file_mod.FileUtil.tmpdir('.cache/teams')
        for file in ('Cookies', 'desktop-config.json'):
            link = os.path.join(tmpdir, file)
            if not os.path.islink(link):
                os.symlink(os.path.join(config_dir, file), link)
        cache_link = os.path.join(
            home,
            '.config',
            'Microsoft',
            'Microsoft Teams',
        )
        if not os.path.islink(cache_link):
            if os.path.isdir(cache_link):
                shutil.rmtree(cache_link)
            os.symlink(tmpdir, cache_link)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        teams = command_mod.Command('teams', errors='stop')
        teams.set_args(sys.argv[1:])

        cls._config_teams()

        subtask_mod.Exec(teams.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
