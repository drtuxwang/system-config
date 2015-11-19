#!/usr/bin/env python3
"""
Wrapper for 'gqview' command
"""

import glob
import os
import signal
import shutil
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options:

    def __init__(self, args):
        self._gqview = syslib.Command('geeqie', check=False)
        if self._gqview.isFound():
            self._configGeeqie()
        else:
            self._gqview = syslib.Command('gqview')
            self._configGqview()
        if len(args) == 1:
            self._gqview.setArgs([os.curdir])
        else:
            self._gqview.setArgs(args[1:])

    def getGqview(self):
        """
        Return gqview Command class object.
        """
        return self._gqview

    def _configGeeqie(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.config', 'geeqie')
            if not os.path.isdir(configdir):
                try:
                    os.makedirs(configdir)
                except OSError:
                    return
            file = os.path.join(configdir, 'history')
            if not os.path.isdir(file):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                    os.mkdir(file)
                except (IOError, OSError):
                    pass
            for file in (os.path.join(os.environ['HOME'], '.local', 'share', 'geeqie'),
                         os.path.join(os.environ['HOME'], '.cache', 'geeqie', 'thumbnails')):
                if not os.path.isfile(file):
                    try:
                        if os.path.isdir(file):
                            shutil.rmtree(file)
                        with open(file, 'wb'):
                            pass
                    except (IOError, OSError):
                        pass

    def _configGqview(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.gqview')
            if not os.path.isdir(configdir):
                try:
                    os.makedirs(configdir)
                except OSError:
                    return
            for directory in ('collections', 'history', 'metadata', 'thumbnails'):
                file = os.path.join(configdir, directory)
                if not os.path.isfile(file):
                    try:
                        if os.path.isdir(file):
                            shutil.rmtree(file)
                        with open(file, 'wb'):
                            pass
                    except (IOError, OSError):
                        pass
            file = os.path.join(configdir, 'history')
            if not os.path.isdir(file):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                    os.mkdir(file)
                except (IOError, OSError):
                    pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            # Geeqie hangs with filter/background
            options.getGqview().run(mode='daemon')
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
