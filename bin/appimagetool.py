#!/usr/bin/env python3
"""
Sandbox for "appimagetool" launcher (allowing non systems port)
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

        appimagetool = network_mod.Sandbox(name, errors='stop')
        appimagetool.set_args(sys.argv[1:])

        if not os.path.isfile(appimagetool.get_file() + '.py'):
            work_dir = os.environ['PWD']
            if work_dir == os.environ['HOME']:
                desktop = os.path.join(work_dir, 'Desktop')
                if os.path.isdir(desktop):
                    os.chdir(desktop)
                    work_dir = desktop
            configs = [work_dir]
            if os.path.realpath(work_dir) != work_dir:
                configs.append(os.path.realpath(work_dir))
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                appimagetool.set_args(sys.argv[2:])
                configs.append('net')

            appimagetool.sandbox(configs)

        subtask_mod.Exec(appimagetool.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
