#!/usr/bin/env python3
"""
Wrapper for 'wget' command
"""

import glob
import os
import signal
import sys

import netnice
import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._wget = syslib.Command('wget')
        self._wget.set_flags(['--no-check-certificate', '--timestamping'])

        shaper = netnice.Shaper()
        if shaper.is_found():
            self._wget.set_wrapper(shaper)

        self._output = ''
        while len(args) > 1:
            if (len(args) > 2 and args[1] in ('--output-document', '-O') and
                    not args[2].endswith('.part')):
                self._output = args[2]
                if os.path.isfile(args[2]) or os.path.isfile(args[2] + '.part'):
                    self._output = ('-'+str(os.getpid())+'.').join(self._output.rsplit('.', 1))
                self._wget.extend_args([args[1], self._output + '.part'])
                args = args[2:]
                continue
            self._wget.append_arg(args[1])
            args = args[1:]

    def get_output(self):
        """
        Return output file.
        """
        return self._output

    def get_wget(self):
        """
        Return wget Command class object.
        """
        return self._wget


class Download(object):
    """
    Download class
    """

    def __init__(self, options):
        self._output = options.get_output()
        self._wget = options.get_wget()

    def run(self):
        """
        Start download
        """
        if self._output:
            self._wget.run()
            if self._wget.get_exitcode():
                raise SystemExit(self._wget.get_exitcode())
            try:
                os.rename(self._output + '.part', self._output)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + self._output + '" output file.')
        else:
            self._wget.run(mode='exec')


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
            Download(options).run()
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
