#!/usr/bin/env python3
"""
Wrapper for "xz" command
"""

import glob
import os
import signal
import sys

import command_mod
import file_mod
import subtask_mod

VERBOSE_SIZE = 134217728


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
        command = command_mod.Command('xz', errors='stop')
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            command.set_args([
                '-9',
                '-e',
                '--lzma2=dict=128MiB',
                '--threads=1'
            ])
            if file_mod.FileStat(sys.argv[1]).get_size() > VERBOSE_SIZE:
                command.append_arg('--verbose')
        command.extend_args(sys.argv[1:])
        self._set_libraries(command)

        subtask_mod.Exec(command.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
