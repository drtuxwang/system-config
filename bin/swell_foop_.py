#!/usr/bin/env python3
"""
Sandbox for "swell-foop" command
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
        command = network_mod.Sandbox(
            '/usr/games/swell-foop',
            args=sys.argv[1:],
            errors='stop'
        )

        # Start slow for very large history (.local/share/swell-foop/)
        if not os.path.isfile(command.get_file() + '.py'):
            configs = [
                '/dev/dri',
                f'/run/user/{os.getuid()}/dconf',
                os.path.join(os.getenv('HOME', '/'), '.config/dconf/user'),
            ]
            command.sandbox(configs)

        subtask_mod.Background(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
