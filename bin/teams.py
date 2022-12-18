#!/usr/bin/env python3
"""
Wrapper for "teams" command
"""

import glob
import os
import shutil
import signal
import sys
from pathlib import Path

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
    def _config_teams() -> None:
        path = Path(Path.home(), '.config', 'autostart', 'teams.desktop')
        if not path.is_dir():
            try:
                if path.is_dir():
                    path.unlink()
                path.mkdir(parents=True)
            except OSError:
                pass

        # Use /tmp cache (keep "Cookies" & "desktop-config.json")
        config_dir = Path(
            Path.home(),
            '.config',
            'Microsoft',
            'Microsoft Teams Config',
        )
        if not config_dir.is_dir():
            config_dir.mkdir(parents=True)
        tmpdir = file_mod.FileUtil.tmpdir('.cache/teams')
        for name in ('Cookies', 'desktop-config.json'):
            link = Path(tmpdir, name)
            if not link.is_symlink():
                link.symlink_to(Path(config_dir, name))
        cache_link = Path(
            Path.home(),
            '.config',
            'Microsoft',
            'Microsoft Teams',
        )
        if not cache_link.is_symlink():
            if cache_link.is_dir():
                shutil.rmtree(cache_link)
            cache_link.symlink_to(tmpdir)

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
