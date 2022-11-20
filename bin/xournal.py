#!/usr/bin/env python3
"""
Sandbox for "xournalpp" launcher
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
        xournal = network_mod.Sandbox('xournalpp', errors='stop')
        xournal.set_args(sys.argv[1:])

        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs = [
            f'/run/user/{os.getuid()}/pulse',
            os.path.join(os.getenv('HOME', '/'), '.config/ibus'),
            os.path.join(os.getenv('HOME', '/'), '.config/xournalpp'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
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
