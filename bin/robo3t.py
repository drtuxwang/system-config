#!/usr/bin/env python3
"""
Wrapper for "robo3t" command
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
    def run() -> None:
        """
        Start program
        """
        name = os.path.basename(sys.argv[0]).replace('.py', '')
        pattern = "QXcbConnection:|libpng warning:"

        robo3t = network_mod.Sandbox(name, errors='stop')
        robo3t.set_args(sys.argv[1:])

        configs = [
            'net',
            '/run/user/{0:d}'.format(os.getuid()),
            os.path.join(os.environ['HOME'], '.3T', 'robo-3t'),
        ]
        work_dir = os.environ['PWD']
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs.append(work_dir)
        robo3t.sandbox(configs)

        subtask_mod.Background(robo3t.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
