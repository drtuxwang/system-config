#!/usr/bin/env python3
"""
Sandbox for "tenacity" launcher
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Background, Exec


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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _config(audacity: Sandbox) -> Path:
        if Path(audacity.get_file()).name == 'tenacity':
            return Path(Path.home(), '.config', 'tenacity')

        audacitydir = Path(Path.home(), '.audacity-data')
        path = Path(audacitydir, 'audacity.cfg')
        if path.is_file():
            if b'ShowSplashScreen=0' not in path.read_bytes():
                with path.open('a', errors='replace') as ofile:
                    print("[GUI]", file=ofile)
                    print("ShowSplashScreen=0", file=ofile)
        return audacitydir

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        audacity = Sandbox('tenacity', errors='ignore')
        if not audacity.is_found():
            audacity = Sandbox('audacity', errors='stop')
        if Path(f'{audacity.get_file()}.py').is_file():
            Exec(audacity.get_cmdline() + sys.argv[1:]).run()

        # "os.getcwd()" returns realpath instead
        work_dir = Path(os.environ['PWD'])
        if work_dir == Path.home():
            desktop = Path(work_dir, 'Desktop')
            if desktop.is_dir():
                os.chdir(desktop)
                work_dir = desktop

        configs = ['/']  # Only block network
        for arg in sys.argv[1:]:
            if arg == '-net':
                configs.append('net')
            else:
                audacity.append_arg(arg)

        audacity.sandbox(configs)

        pattern = (
            '^$|: (Gdk|GdkPixbuf|GLib-GObject)-|[.]so|: invalid (image|bitmap)'
        )

        cmdline = audacity.get_cmdline()
        Background(cmdline).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
