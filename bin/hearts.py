#!/usr/bin/env python3
"""
Sandbox for "hearts" launcher
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

        hearts = network_mod.Sandbox(name, errors='stop')
        hearts.set_args(sys.argv[1:])

        if not os.path.isfile(hearts.get_file() + '.py'):
            configs = [
                '/dev/dri',
                '/dev/shm',
                f'/run/user/{os.getuid()}/pulse',
            ]
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                hearts.set_args(sys.argv[2:])
                configs.append('net')
            hearts.sandbox(configs)

        pattern = 'deprecation:'
        subtask_mod.Task(hearts.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
