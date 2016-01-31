#!/usr/bin/env python3
"""
Wrapper for Nifty Host Selector 'nhs' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
    def _config():
        if 'HOME' in os.environ:
            home = os.environ['HOME']
            if os.path.basename(home) != '.nhs':
                home = os.path.join(home, '.nhs')
                if not os.path.isdir(home):
                    try:
                        os.mkdir(home)
                    except OSError:
                        return
                os.environ['HOME'] = home

    def run(self):
        """
        Start program
        """
        nhs = syslib.Command('nhs')
        nhs.set_args(sys.argv[1:])
        self._config()

        nhs.run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
