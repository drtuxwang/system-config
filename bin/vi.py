#!/usr/bin/env python3
"""
Wrapper for 'vi' command
"""

import glob
import os
import signal
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
    def run():
        """
        Start program
        """
        if os.path.isfile('/usr/bin/vim'):
            command = command_mod.Command('vim', errors='stop')
            if '-n' not in sys.argv[1:]:
                command.set_args(['vim', '-N', '-n', '-i', 'NONE', '-T', 'xterm'])
        else:
            command = command_mod.Command('vi', errors='stop')

        task = subtask_mod.Task(command.get_cmdline() + sys.argv[1:])
        task.run()
        if task.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) + ' received from "' +
                  task.get_file() + '".', file=sys.stderr)
            raise SystemExit(task.get_exitcode())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
