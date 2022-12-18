#!/usr/bin/env python3
"""
Sandbox for "xournalpp" launcher
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
        xournal = network_mod.Sandbox('xournalpp', errors='stop')
        xournal.set_args(sys.argv[1:])

        work_dir = Path.cwd()  # "os.getcwd()" returns realpath instead
        home = str(Path.home())
        if work_dir == home:
            desktop = Path(work_dir, 'Desktop')
            if desktop.is_dir():
                os.chdir(desktop)
                work_dir = desktop

        configs = [
            f'/run/user/{os.getuid()}/pulse',
            Path(home, '.config/ibus'),
            Path(home, '.config/xournalpp'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if Path(sys.argv[1]).is_dir():
                configs.append(Path(sys.argv[1]).resolve())
            elif Path(sys.argv[1]).is_file():
                configs.append(Path(sys.argv[1]).resolve().parent)
            if sys.argv[1] == '-net':
                xournal.set_args(sys.argv[2:])
                configs.append('net')
        xournal.sandbox(configs)

        pattern = (
            '^$|: Gtk-WARNING|: dbind-WARNING|^ALSA|^[jJ]ack|^Cannot connect|'
            ': TEXTDOMAINDIR|: Plugin| does not exist|: No such file|'
            r'No device found|not finding devices!| defaults\['
        )
        subtask_mod.Background(xournal.get_cmdline()).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
