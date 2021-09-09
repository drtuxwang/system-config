#!/usr/bin/env python3
"""
Sandbox for "soffice" launcher
"""

import glob
import os
import shutil
import signal
import sys

import network_mod
import subtask_mod


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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

    def _config(self) -> None:
        for file in glob.glob('.~lock.*#'):  # Remove stupid lock files
            try:
                os.remove(file)
            except OSError:
                pass
        home = os.environ.get('HOME', '')
        for file in glob.glob(os.path.join(
                home,
                '.config',
                'libreoffice',
                '*',
                'user',
                'registrymodifications.xcu'
        )):
            if os.path.isfile(file):
                try:
                    os.remove(file)
                    os.mkdir(file)
                except OSError:
                    pass

        # Remove insecure macros scripting
        try:
            shutil.rmtree(os.path.join(
                os.path.dirname(os.path.dirname(self._soffice.get_file())),
                'share',
                'Scripts',
            ))
        except OSError:
            pass

        # Disable update nagging
        for file in glob.glob(os.path.join(
                os.path.dirname(self._soffice.get_file()),
                'libupd*.so',
        )):
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    def _setenv() -> None:
        if 'GTK_MODULES' in os.environ:
            # Fix Linux 'gnomebreakpad' problems
            del os.environ['GTK_MODULES']

    def run(self) -> int:
        """
        Start program
        """
        self._soffice = network_mod.Sandbox(
            os.path.join('program', 'soffice'),
            errors='stop'
        )
        self._soffice.set_args(['--nologo'] + sys.argv[1:])
        if os.path.isfile(self._soffice.get_file() + '.py'):
            subtask_mod.Exec(self._soffice.get_cmdline()).run()
        if sys.argv[1:] == ['--version']:
            subtask_mod.Exec(self._soffice.get_cmdline()).run()

        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs = [
            '/run/user/{0:d}'.format(os.getuid()),
            os.path.join(os.getenv('HOME', '/'), '.config', 'libreoffice'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
            if sys.argv[1] == '-net':
                self._soffice.set_args(['--nologo'] + sys.argv[2:])
                configs.append('net')
        self._soffice.sandbox(configs)

        self._pattern = (
            '^$|: GLib-CRITICAL |: GLib-GObject-WARNING |: G[dt]k-WARNING |'
            ': wrong ELF class:|: Could not find a Java Runtime|'
            ': failed to read path from javaldx|^Failed to load module:|'
            'unary operator expected|: unable to get gail version number|'
            'gtk printer|: GConf-WARNING|: Connection refused|GConf warning: '
            '|GConf Error: |: invalid source position|:'
        )
        self._config()
        self._setenv()

        cmdline = self._soffice.get_cmdline()
        subtask_mod.Background(cmdline).run(pattern=self._pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
