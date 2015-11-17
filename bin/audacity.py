#!/usr/bin/env python3
"""
Wrapper for 'audacity' command
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
        self._audacity = syslib.Command('audacity')
        self._audacity.setArgs(args[1:])
        self._filter = ('^$|^HCK OnTimer|: Gtk-WARNING | LIBDBUSMENU-GLIB-WARNING |'
                        '^ALSA lib |alsa.c|^Cannot connect to server socket|^jack server')
        self._config()

    def getAudacity(self):
        """
        Return audacity Command class object.
        """
        return self._audacity

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def _config(self):
        if 'HOME' in os.environ:
            audacitydir = os.path.join(os.environ['HOME'], '.audacity-data')
            if not os.path.isdir(audacitydir):
                try:
                    os.mkdir(audacitydir)
                except OSError:
                    pass
                else:
                    if not os.path.isfile(os.path.join(audacitydir, 'audacity.cfg')):
                        with open(os.path.join(audacitydir, 'audacity.cfg'),
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
            options.getAudacity().run(filter=options.getFilter(), mode='background')
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
