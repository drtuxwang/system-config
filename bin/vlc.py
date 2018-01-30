#!/usr/bin/env python3
"""
Wrapper for "vlc" command
"""

import glob
import os
import shutil
import signal
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

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_vlc(self):
        """
        Return vlc Command class object.
        """
        return self._vlc

    @staticmethod
    def _config():
        home = os.environ.get('HOME', '')

        file = os.path.join(home, '.cache', 'vlc')
        if not os.path.isfile(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                with open(file, 'wb'):
                    pass
            except OSError:
                pass

        file = os.path.join(home, '.config', 'vlc', 'vlc-qt-interface.conf')
        try:
            with open(file, errors='replace') as ifile:
                with open(file + '-new', 'w', newline='\n') as ofile:
                    for line in ifile:
                        if line.startswith('geometry='):
                            print(
                                'geometry=@ByteArray(\\x1\\xd9\\xd0\\xcb'
                                '\\0\\x1\\0\\0\\0\\0\\0z\\0\\0\\0\\x32\\0'
                                '\\0\\x2\\x62\\0\\0\\0~\\0\\0\\0z\\0\\0\\0'
                                '\\x32\\0\\0\\x2\\x62\\0\\0\\0~\\0\\0\\0'
                                '\\0\\0\\0)',
                                file=ofile
                            )
                        else:
                            print(line, file=ofile)
        except OSError:
            try:
                os.remove(file + '-new')
            except OSError:
                pass
        else:
            try:
                shutil.move(file + '-new', file)
            except OSError:
                pass

    def parse(self, args):
        """
        Parse arguments
        """
        self._vlc = command_mod.Command('vlc', errors='stop')
        self._vlc.set_args(args[1:])
        self._pattern = ': Paint device returned engine'
        self._config()


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

        subtask_mod.Background(options.get_vlc().get_cmdline()).run(
            pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
