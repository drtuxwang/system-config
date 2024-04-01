#!/usr/bin/env python3
"""
Sandbox for "appimagetool" launcher (allowing non systems port)
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Exec


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
    def run() -> None:
        """
        Start program
        """
        name = Path(sys.argv[0]).stem

        appimagetool = Sandbox(name, errors='stop')

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

            for arg in sys.argv[1:]:
                path = Path(arg).resolve()
                if arg == '-net':
                    configs.append('net')
                elif path.is_dir():
                    appimagetool.append_arg(path)
                    configs.append(path)
                elif path.is_file():
                    appimagetool.append_arg(path)
                    configs.append(path.parent)
                else:
                    appimagetool.append_arg(arg)

            appimagetool.sandbox(configs)

        Exec(appimagetool.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
