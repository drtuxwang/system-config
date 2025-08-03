#!/usr/bin/env python3
"""
Sandbox for "inkscape" launcher
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Daemon, Exec


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
    def run() -> int:
        """
        Start program
        """
        inkscape = Sandbox('inkscape', errors='stop')
        if Path(f'{inkscape.get_file()}.py').is_file():
            Exec(inkscape.get_cmdline() + sys.argv[1:]).run()

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
                inkscape.append_arg(arg)

        inkscape.sandbox(configs)

        Daemon(inkscape.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
