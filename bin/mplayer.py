#!/usr/bin/env python3
"""
Wrapper for 'mplayer' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options:

    def __init__(self, args):
        self._config()
        if os.name == 'nt':
            self._mplayer = syslib.Command('mplayer.exe')
        else:
            self._mplayer = syslib.Command('mplayer')
        self._mplayer.setFlags([
            '-msglevel', 'all=0', '-alang', 'en', '-slang', 'en', '-monitoraspect', '4:3'])
        if syslib.Task().haspname('pulseaudio'):
            self._mplayer.extendFlags(['-ao', 'pulse'])
        else:
            self._mplayer.extendFlags(['-ao', 'alsa'])
        self._mplayer.setArgs(args[1:])
        if len(self._mplayer.getArgs()):
            if self._mplayer.getArgs()[0].split('.')[-1] in ('.asf', '.asx', '.ram'):
                self._mplayer.appendFlag('-playlist')  # Avoid 'avisynth.dll' error
        self._setLibraries(self._mplayer)

    def getMplayer(self):
        """
        Return mplayer Command class object.
        """
        return self._mplayer

    def _config(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.mplayer')
            if not os.path.isdir(configdir):
                try:
                    os.makedirs(configdir)
                except OSError:
                    return
            os.chmod(configdir, int('700', 8))
            if not os.path.isfile(os.path.join(configdir, 'config')):
                try:
                    with open(os.path.join(configdir, 'config'), 'w', newline='\n') as ofile:
                        print('# Write your default config options here!\n', file=ofile)
                        print('prefer-ipv4 = yes', file=ofile)
                        print('\n[gnome-mplayer]', file=ofile)
                        print('msglevel=all=0', file=ofile)
                        print('vo=x11', file=ofile)
                        print('vf=eq2', file=ofile)
                        print('zoom=1', file=ofile)
                except IOError:
                    return

    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), 'lib')
        if os.path.isdir(libdir):
            if 'LD_LIBRARY_PATH' in os.environ:
                os.environ['LD_LIBRARY_PATH'] = libdir + os.pathsep + os.environ['LD_LIBRARY_PATH']
            else:
                os.environ['LD_LIBRARY_PATH'] = libdir
            if self._mplayer.flags[-1] in ('pulse', 'alsa'):
                self._mplayer.flags[-1] = 'esd'


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getMplayer().run(mode='exec')
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
