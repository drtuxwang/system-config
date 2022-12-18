#!/usr/bin/env python3
"""
Sandbox for "appimagetool" launcher (allowing non systems port)
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
    def run() -> None:
        """
        Start program
        """
        name = Path(sys.argv[0]).stem

        appimagetool = network_mod.Sandbox(name, errors='stop')
        appimagetool.set_args(sys.argv[1:])

        if not Path(f'{appimagetool.get_file()}.py').is_file():
            work_dir = Path(os.environ['PWD'])
            if work_dir == Path.home():
                desktop = Path(work_dir, 'Desktop')
                if desktop.is_dir():
                    os.chdir(desktop)
                    work_dir = desktop

            configs: list = [work_dir]
            if Path(work_dir).resolve() != work_dir:
                configs.append(Path(work_dir).resolve())
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
