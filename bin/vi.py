#!/usr/bin/env python3
"""
Wrapper for 'vi' command
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
    def _edit(command):
        command.run()
        if command.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(command.get_exitcode()) + ' received from "' +
                  command.get_file() + '".', file=sys.stderr)
            raise SystemExit(command.get_exitcode())

    def run(self):
        """
        Start program
        """
        if os.path.isfile('/usr/bin/vim'):
            command = syslib.Command('vim')
        else:
            command = syslib.Command('vi')

        command.set_args(sys.argv[1:])
        if len(sys.argv) > 1 and sys.argv[-1] != 'NONE':
            try:
                sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' +
                                 os.path.abspath(sys.argv[1] + '\007'))
            except OSError:
                pass
            else:
                sys.stdout.flush()
                self._edit(command)
                sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':\007')
        else:
            self._edit(command)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
