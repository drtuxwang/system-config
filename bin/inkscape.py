#!/usr/bin/env python3
"""
Sandbox for "inkscape" launcher
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
        inkscape = network_mod.Sandbox('inkscape', errors='stop')
        inkscape.set_args(sys.argv[1:])
        if os.path.isfile(inkscape.get_file() + '.py'):
            subtask_mod.Exec(inkscape.get_cmdline()).run()

        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs = [
            os.path.join(os.getenv('HOME', '/'), '.config/ibus'),
            os.path.join(os.getenv('HOME', '/'), '.config/inkscape'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
            if sys.argv[1] == '-net':
                inkscape.set_args(sys.argv[2:])
                configs.append('net')
        inkscape.sandbox(configs)

        subtask_mod.Daemon(inkscape.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
