#!/usr/bin/env python3
"""
Sandbox for "vlc" launcher
"""

import glob
import os
import shutil
import signal
import sys
from typing import List

import network_mod
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

    def get_vlc(self) -> network_mod.Sandbox:
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
        self._vlc = network_mod.Sandbox('vlc', errors='stop')
        self._vlc.set_args(args[1:])
        if os.path.isfile(self._vlc.get_file() + '.py'):
            subtask_mod.Exec(self._vlc.get_cmdline()).run()

        configs = [
            '/dev/dri',
            '/dev/shm',
            os.path.join(os.getenv('HOME', '/'), '.config/vlc'),
        ]
        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if os.environ['PWD'] == os.environ['HOME']:
            desktop = os.path.join(os.environ['HOME'], 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        if 'dvdsimple:' in args:
            configs.append(work_dir)
        else:
            configs.append(work_dir + ':ro')
        if len(args) >= 2:
            if os.path.isdir(args[1]):
                configs.append(os.path.abspath(args[1]) + ':ro')
            elif os.path.isfile(args[1]):
                configs.append(
                    os.path.dirname(os.path.abspath(args[1])) + ':ro',
                )
            if sys.argv[1] == '-net':
                self._vlc.set_args(args[2:])
                configs.append('net')
        self._vlc.sandbox(configs)

        if len(args) >= 2 and args[1].startswith('-') and args[1] != '-net':
            subtask_mod.Exec(self._vlc.get_cmdline()).run()

        self._pattern = (
            ': Paint device returned engine|: playlist is empty|'
            ': Timers cannot|: Running vlc with the default|Qt: Session'
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
            sys.exit(exception)

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
