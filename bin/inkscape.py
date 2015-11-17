#!/usr/bin/env python3
"""
Wrapper for 'inkscape' command
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
        self._inkscape = syslib.Command('inkscape')
        self._inkscape.setArgs(args[1:])
        self._filter = '^$|: Gtk-CRITICAL|: GLib-GObject-|: Gtk-WARNING|: WARNING'
        self._config()

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getInkscape(self):
        """
        Return inkscape Command class object.
        """
        return self._inkscape

    def _config(self):
        if 'HOME' in os.environ:
            inkscapedir = os.path.join(os.environ['HOME'], '.inkscape-data')
            if not os.path.isdir(inkscapedir):
                try:
                    os.mkdir(inkscapedir)
                except OSError:
                    pass
                else:
                    if not os.path.isfile(os.path.join(inkscapedir, 'inkscape.cfg')):
                        with open(os.path.join(inkscapedir, 'inkscape.cfg'),
                                  'w', newline='\n') as ofile:
                            print('[AudioIO]', file=ofile)
                            print('PlaybackDevice=ALSA: pulse', file=ofile)
                            print('RecordingDevice=ALSA: pulse', file=ofile)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getInkscape().run(filter=options.getFilter(), mode='background')
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
