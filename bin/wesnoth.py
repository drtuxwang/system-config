#!/usr/bin/env python3
"""
Sandbox for "wesnoth" launcher
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

        wesnoth = network_mod.Sandbox(name, errors='stop')
        wesnoth.set_args(sys.argv[1:])

        if not os.path.isfile(wesnoth.get_file() + '.py'):
            configs = [
                '/dev/dri',
                '/dev/shm',
                f'/run/user/{os.getuid()}/pulse',
            ]
            configs.extend(glob.glob(os.path.join(
                os.getenv('HOME', '/'),
                '.config/wesnoth*',
            )))
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                wesnoth.set_args(sys.argv[2:])
                configs.append('net')
            wesnoth.sandbox(configs)

        pattern = 'deprecation:'
        subtask_mod.Task(wesnoth.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
