#!/usr/bin/env python3
"""
Wrapper for "aria2c" command
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from network_mod import NetNice
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
    def _set_libraries(command: Command) -> None:
        libdir = Path(Path(command.get_file()).parent, 'lib')
        if libdir.is_dir():
            if os.name != 'nt' and os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        f"{libdir}{os.pathsep}{os.environ['LD_LIBRARY_PATH']}"
                    )
                else:
                    os.environ['LD_LIBRARY_PATH'] = str(libdir)

    def run(self) -> int:
        """
        Start program
        """
        aria2c = Command('aria2c', errors='stop')
        self._set_libraries(aria2c)
        args = sys.argv[1:]
        if '--remote-time=true' not in args:
            aria2c.set_args(['--remote-time=true'] + args)
        else:
            aria2c.set_args(args)

        cmdline = aria2c.get_cmdline()
        netnice = NetNice()
        if netnice.is_found():
            cmdline = netnice.get_cmdline() + cmdline
        Exec(cmdline).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
