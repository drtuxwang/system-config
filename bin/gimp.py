#!/usr/bin/env python3
"""
Wrapper for 'gimp' command
"""

import glob
import os
import shutil
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
        self._gimp = syslib.Command('gimp')
        self._gimp.set_args(args[1:])
        self._filter = ('^$| GLib-WARNING | GLib-GObject-WARNING | Gtk-WARNING |: Gimp-|'
                        ' g_bookmark_file_get_size:|recently-used.xbel|^ sRGB |^lcms: |'
                        'pixmap_path: |in <module>| import |wrong ELF class:|'
                        ': LibGimpBase-WARNING |^Traceback |: undefined symbol:| XMP metadata:|'
                        ': No XMP packet found')
        self._config()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_gimp(self):
        """
        Return gimp Command class object.
        """
        return self._gimp

    def _config(self):
        if 'HOME' in os.environ:
            if os.path.isdir(os.path.join(os.environ['HOME'], '.thumbnails')):
                try:
                    shutil.rmtree(os.path.join(os.environ['HOME'], '.thumbnails'))
                except OSError:
                    pass
            for file in glob.glob(os.path.join(os.environ['HOME'], '.gimp*', 'gimprc')):
                try:
                    with open(file, errors='replace') as ifile:
                        if '(thumbnail-size none)\n' not in ifile.readlines():
                            with open(file, 'a', newline='\n') as ofile:
                                print('(thumbnail-size none)', file=ofile)
                except OSError:
                    continue


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
            options.get_gimp().run(filter=options.get_filter(), mode='background')
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
