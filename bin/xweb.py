#!/usr/bin/env python3
"""
Start web browser
"""

import glob
import os
import signal
import sys

import command_mod
import config_mod
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
    def _get_default() -> str:
        home = os.environ.get('HOME', '')
        file = os.path.join(home, 'software', 'web-data', 'index.xhtml')
        if os.path.isfile(file):
            return file

        return config_mod.Config().get('homepage')

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
        browser, *flags = config_mod.Config().get_app('web_browser')[0]
        command = command_mod.Command(browser, args=flags, errors='stop')
        if len(sys.argv) > 1:
            command.set_args(sys.argv[1:])
        else:
            command.set_args([cls._get_default()] * cls._get_tabs())
        subtask_mod.Task(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
