#!/usr/bin/env python3
"""
WOLFENSTEIN ENEMY TERRITORY game launcher
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
        self._et = syslib.Command('et.x86', check=False)
        if not os.path.isfile(self._et.get_file()):
            self._et = syslib.Command('et')
            self._et.set_args(args[1:])
            self._et.run(mode='exec')
        xrun = syslib.Command('xrun', check=False)
        if xrun.is_found():
            self._et.set_wrapper(xrun)
        self._config()
        self._punkbuster()
        self._et.set_args(args[1:])

    def getEt(self):
        """
        Return et Command class object.
        """
        return self._et

    def get_logfile(self):
        """
        Return logfile location.
        """
        return self._logfile

    def _punkbuster(self):
        if 'HOME' in os.environ:
            pbdir = os.path.join(os.environ['HOME'], '.etwolf', 'pb')
            linkdir = os.path.join(os.path.dirname(self._et.get_file()), 'pb')
            if not os.path.islink(pbdir):
                if os.path.isdir(pbdir):
                    try:
                        shutil.rmtree(pbdir)
                    except OSError:
                        return
            elif os.readlink(pbdir) != linkdir:
                os.remove(pbdir)
            if not os.path.islink(pbdir):
                try:
                    os.symlink(linkdir, pbdir)
                except OSError:
                    pass
            if not os.access(os.path.join(pbdir, 'pbcl.so'), os.R_OK):
                raise SystemExit(sys.argv[0] + ': Cannot access "pbcl.so" in "' +
                                 pbdir + '" directory.')
            etkey = os.path.join(os.environ['HOME'], '.etwolf', 'etmain', 'etkey')
            if not os.path.isfile(etkey):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + etkey +
                                 '" key file (see http://www.etkey.net).')

    def _config(self):
        os.chdir(os.path.dirname(self._et.get_file()))
        if 'HOME' in os.environ:
            os.environ['SDL_AUDIODRIVER'] = 'pulse'
            etsdl = (glob.glob('/usr/lib/i386-linux-gnu/libSDL-*so*') +
                     glob.glob('/usr/lib32/libSDL-*so*') +
                     glob.glob('/usr/lib/libSDL-*so*'))
            if not etsdl:
                raise SystemExit(sys.argv[0] + ": Cannot find SDL sound interface library.")
            os.environ['ETSDL_SDL_LIB'] = etsdl[0]
            if 'LD_PRELOAD' in os.environ:
                os.environ['LD_PRELOAD'] = (os.environ['LD_PRELOAD'] + os.pathsep + os.path.join(
                    os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so'))
            else:
                os.environ['LD_PRELOAD'] = os.path.join(
                    os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so')
            if not os.path.isdir(os.path.join(os.environ['HOME'], '.etwolf')):
                os.mkdir(os.path.join(os.environ['HOME'], '.etwolf'))
            self._logfile = os.path.join(os.environ['HOME'], '.etwolf', 'etwolf.log')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        try:
            options = Options(sys.argv)
            options.getEt().run(logfile=options.get_logfile(), mode='daemon')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
