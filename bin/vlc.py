#!/usr/bin/env python3
"""
Wrapper for 'vlc' command
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
        self._vlc = syslib.Command('vlc')
        self._vlc.set_args(args[1:])
        self._filter = ': Paint device returned engine'
        self._config()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_vlc(self):
        """
        Return vlc Command class object.
        """
        return self._vlc

    def _config(self):
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.config', 'vlc', 'vlc-qt-interface.conf')
            try:
                with open(file, errors='replace') as ifile:
                    with open(file + '-new', 'w', newline='\n') as ofile:
                        for line in ifile:
                            if line.startswith('geometry='):
                                print('geometry=@ByteArray(\\x1\\xd9\\xd0\\xcb\\0\\x1\\0\\0\\0\\0'
                                      '\\0z\\0\\0\\0\\x32\\0\\0\\x2\\x62\\0\\0\\0~\\0\\0\\0z\\0'
                                      '\\0\\0\\x32\\0\\0\\x2\\x62\\0\\0\\0~\\0\\0\\0\\0\\0\\0)',
                                      file=ofile)
                            else:
                                print(line, file=ofile)
            except IOError:
                try:
                    os.remove(file + '-new')
                except OSError:
                    pass
            else:
                try:
                    os.rename(file + '-new', file)
                except OSError:
                    pass


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
            options.get_vlc().run(filter=options.get_filter(), mode='background')
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
