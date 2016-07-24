#!/usr/bin/env python3
"""
WOLFENSTEIN ENEMY TERRITORY game launcher
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

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
                raise SystemExit(
                    sys.argv[0] + ': Cannot access "pbcl.so" in "' +
                    pbdir + '" directory.'
                )
            etkey = os.path.join(
                os.environ['HOME'], '.etwolf', 'etmain', 'etkey')
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
                raise SystemExit(
                    sys.argv[0] + ": Cannot find SDL sound interface library.")
            os.environ['ETSDL_SDL_LIB'] = etsdl[0]
            if 'LD_PRELOAD' in os.environ:
                os.environ['LD_PRELOAD'] = (
                    os.environ['LD_PRELOAD'] + os.pathsep + os.path.join(
                        os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so')
                )
            else:
                os.environ['LD_PRELOAD'] = os.path.join(
                    os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so')
            if not os.path.isdir(os.path.join(
                    os.environ['HOME'], '.etwolf')):
                os.mkdir(os.path.join(os.environ['HOME'], '.etwolf'))

    def run(self):
        """
        Start program
        """
        self._et = command_mod.Command('et.x86', errors='ignore')
        if not os.path.isfile(self._et.get_file()):
            self._et = command_mod.Command('et', errors='stop')
            self._et.set_args(sys.argv[1:])
            subtask_mod.Exec(self._et.get_cmdline()).run()

        self._config()
        self._punkbuster()
        self._et.set_args(sys.argv[1:])

        logfile = os.path.join(os.environ['HOME'], '.etwolf', 'etwolf.log')
        xrun = command_mod.Command('xrun', errors='ignore')
        if xrun.is_found():
            subtask_mod.Daemon(
                xrun.get_cmdline() + self._et.get_cmdline()).run(file=logfile)
        else:
            subtask_mod.Daemon(self._et.get_cmdline()).run(file=logfile)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
