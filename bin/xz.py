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
    def _set_libraries(command: command_mod.Command) -> None:
        libdir = os.path.join(os.path.dirname(command.get_file()), 'lib')
        if os.path.isdir(libdir):
            if os.name != 'nt' and os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        command = command_mod.Command('xz', errors='stop')
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            command.set_args([
                '-9',
                '-e',
                '--x86',
                '--lzma2=dict=128MiB',
                '--threads=1'
            ])
            for file in sys.argv[1:]:
                if file_mod.FileStat(file).get_size() > VERBOSE_SIZE:
                    command.append_arg('--verbose')
                    break
        command.extend_args(sys.argv[1:])
        cls._set_libraries(command)

        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
