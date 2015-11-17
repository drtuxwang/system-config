#!/usr/bin/env python3
"""
Wrapper for 'vi' command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        if os.path.isfile('/usr/bin/vim'):
            self._vi = syslib.Command('vim')
        else:
            self._vi = syslib.Command('vi')

        self._vi.setArgs(args[1:])
        if len(args) > 1 and args[-1] != 'NONE':
            self._file = args[-1]
        else:
            self._file = None

    def getFile(self):
        """
        Return file.
        """
        return self._file

    def getVi(self):
        """
        Return vi Command class object.
        """
        return self._vi


class Edit(syslib.Dump):

    def __init__(self, options):
        if options.getFile():
            try:
                sys.stdout.write('\033]0;' + syslib.info.getHostname() + ':' +
                                 os.path.abspath(options.getFile()) + '\007')
            except OSError:
                pass
            else:
                sys.stdout.flush()
                self._edit(options)
                sys.stdout.write('\033]0;' + syslib.info.getHostname() + ':\007')
        else:
            self._edit(options)

    def _edit(self, options):
        vi = options.getVi()
        vi.run()
        if vi.getExitcode():
            print(sys.argv[0] + ': Error code ' + str(vi.getExitcode()) + ' received from "' +
                  vi.getFile() + '".', file=sys.stderr)
            raise SystemExit(vi.getExitcode())


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
