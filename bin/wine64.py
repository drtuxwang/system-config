#!/usr/bin/env python3
"""
Wrapper for "wine" & "wine64" command

Use "-reset" to clean ".wine" junk
"""

import glob
import os
import signal
import shutil
import sys

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """
    _wine = command_mod.Command(
        os.path.basename(sys.argv[0]),
        errors='stop'
    )

    def __init__(self):
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_wine(self):
        """
        Return wine Command class object.
        """
        return self._wine

    @staticmethod
    def _reset():
        home = os.environ.get('HOME', '')
        directory = os.path.join(home, '.wine')
        if os.path.isdir(directory):
            print('Removing "{0:s}"...'.format(directory))
            try:
                shutil.rmtree(directory)
            except OSError:
                pass

    def _signal_ignore(self, sig, frame):
        pass

    @classmethod
    def _config(cls):
        signal.signal(signal.SIGINT, cls._signal_ignore)
        signal.signal(signal.SIGTERM, cls._signal_ignore)
#        os.environ['WINEDLLOVERRIDES'] = os.environ.get(
#            'WINEDLLOVERRIDES',
#            'mscoree,mshtml='
#        )

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) > 1:
            if args[1].endswith('.bat'):
                self._wine.set_args(['cmd', '/c'])
            elif args[1].endswith('.msi'):
                self._wine.set_args(['cmd', '/c', 'start'])
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
        self._wine.extend_args(args[1:])


class Main:
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

        wine = options.get_wine()
        xrandr = command_mod.Command('xrandr', errors='stop')
        task = subtask_mod.Batch(xrandr.get_cmdline())
        task.run(pattern='^  ')
        orig_resolution = 0
        for line in task.get_output():
            if '*' in line:
                break
            orig_resolution += 1

        subtask_mod.Task(wine.get_cmdline()).run()

        task = subtask_mod.Batch(xrandr.get_cmdline())
        task.run(pattern='^  ')
        new_resolution = 0
        for line in task.get_output():
            if '*' in line:
                break
            new_resolution += 1
        if new_resolution != orig_resolution:
            xrandr.set_args(['-s', str(orig_resolution)])
            subtask_mod.Batch(xrandr.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
