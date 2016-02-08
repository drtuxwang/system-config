#!/usr/bin/env python3
"""
Play system bell sound
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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
        if sys.argv[0].endswith('.py'):
            sound = sys.argv[0][:-3] + '.ogg'
        else:
            sound = sys.argv[0] + '.ogg'

        if not os.path.isfile(sound):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + sound + '" file.')
        bell = syslib.Command('ogg123', check=False)
        if not bell.is_found():
            bell = syslib.Command('cvlc', flags=['--play-and-exit'], check=False)
            if not bell.is_found():
                raise SystemExit(sys.argv[0] + ': Cannot find required "ogg123" or'
                                 ' "cvlc" software.')
        bell.set_args([sound])

        bell.run(mode='batch')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
