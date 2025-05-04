#!/usr/bin/env python3
"""
Start web browser
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from config_mod import Config
from subtask_mod import Task


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
    def _get_default() -> str:
        path = Path(Path.home(), 'software', 'web-data', 'index.xhtml')
        if path.is_file():
            return str(path)

        return Config().get('web_homepage')

    @staticmethod
    def _get_tabs() -> int:
        try:
            tabs = int(os.environ['XWEB_TABS'])
            if 1 < tabs < 10:
                return tabs
        except (KeyError, ValueError):
            pass
        return 1

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        browser, *flags = Config().get_app('web_browser')[0]
        command = Command(browser, args=flags, errors='stop')
        if len(sys.argv) > 1:
            command.set_args(sys.argv[1:])
        else:
            command.set_args([cls._get_default()] * cls._get_tabs())
        Task(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
