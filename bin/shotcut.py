#!/usr/bin/env python3
"""
Sandbox for "shotcut" launcher
"""

import glob
import os
import signal
import sys

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
        shotcut = network_mod.Sandbox('shotcut', errors='stop')
        shotcut.set_args(sys.argv[1:])
        if os.path.isfile(shotcut.get_file() + '.py'):
            subtask_mod.Exec(shotcut.get_cmdline()).run()

        home = os.environ['HOME']
        home_videos = os.path.join(home, '.config/Meltytech/Videos')
        if not os.path.isdir(home_videos):
            os.makedirs(home_videos)
        configs = [
            '/dev/dri',
            os.path.join(home, '.config/Meltytech'),
            "{0:s}:{1:s}".format(home_videos, os.path.join(home, 'Videos'))
        ]
        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs.append(work_dir)
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
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
