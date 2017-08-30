#!/usr/bin/env python3
"""
Wrapper for "gqview" command
"""

import glob
import os
import signal
import shutil
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_gqview(self):
        """
        Return gqview Command class object.
        """
        return self._gqview

    @staticmethod
    def _config_geeqie():
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, '.config', 'geeqie')
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
            except OSError:
                pass
        for file in (
                os.path.join(home, '.local', 'share', 'geeqie'),
                os.path.join(home, '.cache', 'geeqie', 'thumbnails')
        ):
            if not os.path.isfile(file):
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    with open(file, 'wb'):
                        pass
                except OSError:
                    pass

    @staticmethod
    def _config_gqview():
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, '.gqview')
        if not os.path.isdir(configdir):
            try:
                os.makedirs(configdir)
            except OSError:
                return
        for directory in (
                'collections', 'history', 'metadata', 'thumbnails'
        ):
            file = os.path.join(configdir, directory)
            if not os.path.isfile(file):
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    with open(file, 'wb'):
                        pass
                except OSError:
                    pass
        file = os.path.join(configdir, 'history')
        if not os.path.isdir(file):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                os.mkdir(file)
            except OSError:
                pass

    def parse(self, args):
        """
        Parse arguments
        """
        self._gqview = command_mod.Command('geeqie', errors='ignore')
        if self._gqview.is_found():
            self._config_geeqie()
        else:
            self._gqview = command_mod.Command('gqview', errors='stop')
            self._config_gqview()
        if len(args) == 1:
            self._gqview.set_args([os.curdir])
        else:
            self._gqview.set_args(args[1:])


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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()
        # Geeqie hangs with filter/background
        subtask_mod.Daemon(options.get_gqview().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
