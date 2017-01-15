#!/usr/bin/env python3
"""
Wrapper for 'aria2c' command
"""

import glob
import os
import signal
import sys

import command_mod
import network_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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
    def _set_libraries(command):
        libdir = os.path.join(os.path.dirname(command.get_file()), 'lib')
        if os.path.isdir(libdir):
            if os.name != 'nt' and os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    def run(self):
        """
        Start program
        """
        aria2c = command_mod.Command('aria2c', errors='stop')
        self._set_libraries(aria2c)
        args = sys.argv[1:]
        if '--remote-time=true' not in args:
            aria2c.set_args(['--remote-time=true'] + args)
        else:
            aria2c.set_args(args)

        shaper = network_mod.Shaper()
        if shaper.is_found():
            subtask_mod.Exec(shaper.get_cmdline() + aria2c.get_cmdline()).run()
        else:
            subtask_mod.Exec(aria2c.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
