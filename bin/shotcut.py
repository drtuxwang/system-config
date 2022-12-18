#!/usr/bin/env python3
"""
Sandbox for "shotcut" launcher
"""

import glob
import os
import signal
import sys
from pathlib import Path

import network_mod
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
    def run() -> int:
        """
        Start program
        """
        shotcut = network_mod.Sandbox('shotcut', errors='stop')
        shotcut.set_args(sys.argv[1:])
        if Path(f'{shotcut.get_file()}.py').is_file():
            subtask_mod.Exec(shotcut.get_cmdline()).run()

        home = str(Path.home())
        home_videos = Path(Path.home(), '.config/Meltytech/Videos')
        if not home_videos.is_dir():
            home_videos.mkdir(parents=True)

        configs = [
            '/dev/dri',
            Path(home, '.config/ibus'),
            Path(home, '.config/Meltytech'),
            f"{home_videos}:{Path(home, 'Videos')}",
        ]
        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == home:
            desktop = Path(work_dir, 'Desktop')
            if desktop.is_dir():
                os.chdir(desktop)
                work_dir = str(desktop)
        configs.append(work_dir)
        if len(sys.argv) >= 2:
            if Path(sys.argv[1]).is_dir():
                configs.append(Path(sys.argv[1]).resolve())
            elif Path(sys.argv[1]).is_file():
                configs.append(Path(sys.argv[1]).resolve().parent)
            if sys.argv[1] == '-net':
                shotcut.set_args(sys.argv[2:])
                configs.append('net')
        shotcut.sandbox(configs)

        subtask_mod.Daemon(shotcut.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
