#!/usr/bin/env python3
"""
Wrapper for 'vim' command
"""

import glob
import os
import signal
import socket
import sys

import command_mod
import subtask_mod

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
    def _edit(command):
        task = subtask_mod.Task(command.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) + ' received from "' +
                  task.get_file() + '".', file=sys.stderr)
            raise SystemExit(task.get_exitcode())

    @staticmethod
    def _create_vimrc():
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.vimrc')
            if not os.path.isfile(file):
                try:
                    with open(file, 'w', newline='\n') as ofile:
                        print('syntax on', file=ofile)
                        print('set background=dark', file=ofile)
                except OSError:
                    pass

    def run(self):
        """
        Start program
        """
        command = command_mod.Command('vim', errors='stop')
        command.set_args(sys.argv[1:])

        self._create_vimrc()

        for file in sys.argv[1:]:
            if not file.startswith('-'):
                host = socket.gethostname().split('.')[0].lower()
                try:
                    sys.stdout.write('\033]0;' + host + ':' + os.path.abspath(file) + '\007')
                except OSError:
                    pass
                else:
                    sys.stdout.flush()
                    self._edit(command)
                    sys.stdout.write('\033]0;' + host + ':\007')
                break
        else:
            self._edit(command)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
