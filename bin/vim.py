#!/usr/bin/env python3
"""
Wrapper for 'vim' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._vim = syslib.Command('vim')
        self._vim.set_args(args[1:])

        if len(args) > 1 and args[-1] != 'NONE':
            self._file = args[-1]
        else:
            self._file = None

    def get_file(self):
        """
        Return file.
        """
        return self._file

    def get_vim(self):
        """
        Return vim Command class object.
        """
        return self._vim


class Edit(object):
    """
    Edit class
    """

    def __init__(self, options):
        if options.get_file():
            try:
                sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' +
                                 os.path.abspath(options.get_file()) + '\007')
            except OSError:
                pass
            else:
                sys.stdout.flush()
                self._edit(options)
                sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':\007')
        else:
            self._edit(options)

    def _edit(self, options):
        command = options.get_vim()
        command.run()
        if command.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(command.get_exitcode()) + ' received from "' +
                  command.get_file() + '".', file=sys.stderr)
            raise SystemExit(command.get_exitcode())


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Edit(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
