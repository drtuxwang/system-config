#!/usr/bin/env python3
"""
Wrapper for "vlc" command
"""

import glob
import os
import shutil
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_vlc(self) -> command_mod.Command:
        """
        Return vlc Command class object.
        """
        return self._vlc

    @staticmethod
    def _config() -> None:
        home = os.environ.get('HOME', '')

        file = os.path.join(home, '.cache', 'vlc')
        if not os.path.isfile(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                with open(file, 'wb'):
                    pass
            except OSError:
                pass

        # Corrupt QT config file nags startup
        try:
            os.remove(
                os.path.join(home, '.config', 'vlc', 'vlc-qt-interface.conf')
            )
        except OSError:
            pass

        # Fix QT 5 button size scaling bug
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
        os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._vlc = command_mod.Command('vlc', errors='stop')
        self._vlc.set_args(args[1:])

        if len(args) >= 2 and args[1].startswith('-'):
            subtask_mod.Exec(self._vlc.get_cmdline()).run()

        self._pattern = (
            ': Paint device returned engine|: playlist is empty|'
            ': Timers cannot|: Running vlc with the default|XCB error:'
        )
        self._config()


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
        options = Options()

        subtask_mod.Background(options.get_vlc().get_cmdline()).run(
            pattern=options.get_pattern()
        )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
