#!/usr/bin/env python3
"""
Wrapper for "curl-impersonate" command
"""

import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command, CommandFile, LooseVersion
from subtask_mod import Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_curl(self) -> Command:
        """
        Return curl Command class object.
        """
        return self._curl

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._curl = Command('curl-impersonate', errors='stop')
        browser = Path(args[0]).stem.split('-')[-1]
        if 'impersonate' not in browser:
            path = Path(self._curl.get_file()).parent
            paths = list(path.glob(f'curl_{browser}*[0-9]'))
            if paths:
                self._curl = CommandFile(sorted(paths, key=LooseVersion)[-1])
            else:
                self._curl = Command(Path(args[0]).stem)
        self._curl.set_args(args[1:])


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
        options = Options()

        curl = options.get_curl()
        Exec(curl.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
