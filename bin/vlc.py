#!/usr/bin/env python3
"""
Wrapper for "vlc" command
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_vlc(self):
        """
        Return vlc Command class object.
        """
        return self._vlc

    @staticmethod
    def _config():
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

    def parse(self, args):
        """
        Parse arguments
        """
        self._vlc = command_mod.Command('vlc', errors='stop')
        self._vlc.set_args(args[1:])
        self._pattern = ': Paint device returned engine'
        self._config()


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def run():
        """
        Start program
        """
        options = Options()

        # Fix QT 5 button size scaling bug
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'

        subtask_mod.Background(options.get_vlc().get_cmdline()).run(
            pattern=options.get_pattern()
        )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
