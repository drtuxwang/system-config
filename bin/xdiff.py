#!/usr/bin/env python3
"""
Graphical file comparison and merge tool.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._meld = syslib.Command('meld')
        files = self._args.files
        if os.path.isdir(files[0]) and os.path.isfile(files[1]):
            self._meld.set_args([os.path.join(files[0], os.path.basename(files[1])), files[1]])
        elif os.path.isfile(files[0]) and os.path.isdir(files[1]):
            self._meld.set_args([files[0], os.path.join(files[1], os.path.basename(files[0]))])
        elif os.path.isfile(files[0]) and os.path.isfile(files[1]):
            self._meld.set_args(args[1:])
        else:
            raise SystemExit(sys.argv[0] + ': Cannot compare two directories.')

        self._filter = ('^$|: GtkWarning: |: Gtk-CRITICAL |^  buttons =|^  gtk.main|'
                        'recently-used.xbel')

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_meld(self):
        """
        Return meld Command class object.
        """
        return self._meld

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Graphical file comparison and merge tool.')

        parser.add_argument('files', nargs=2, metavar='file',
                            help='File to compare.')

        self._args = parser.parse_args(args)


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
            options.get_meld().run(filter=options.get_filter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.get_meld().get_exitcode())

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
