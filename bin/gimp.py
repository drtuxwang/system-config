#!/usr/bin/env python3
"""
Wrapper for "gimp" command
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod


class Options:
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

    def get_gimp(self):
        """
        Return gimp Command class object.
        """
        return self._gimp

    @staticmethod
    def _config():
        home = os.environ.get('HOME', '')

        file = os.path.join(home, '.cache', 'thumbnails')
        if not os.path.isfile(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                with open(file, 'wb'):
                    pass
            except OSError:
                pass

        if os.path.isdir(os.path.join(home, '.thumbnails')):
            try:
                shutil.rmtree(os.path.join(home, '.thumbnails'))
            except OSError:
                pass
        for file in glob.glob(
                os.path.join(home, '.gimp*', 'gimprc')):
            try:
                with open(file, errors='replace') as ifile:
                    if '(thumbnail-size none)\n' not in ifile.readlines():
                        with open(file, 'a', newline='\n') as ofile:
                            print("(thumbnail-size none)", file=ofile)
            except OSError:
                continue

    def parse(self, args):
        """
        Parse arguments
        """
        self._gimp = command_mod.Command('gimp', errors='stop')
        self._gimp.set_args(args[1:])
        self._pattern = (
            '^$| GLib-WARNING | GLib-GObject-WARNING | Gtk-WARNING |: Gimp-|'
            ' g_bookmark_file_get_size:|recently-used.xbel|^ sRGB |^lcms: |'
            'pixmap_path: |in <module>| import |wrong ELF class:|'
            ': LibGimpBase-WARNING |^Traceback |: undefined symbol:|'
            ' XMP metadata:|: No XMP packet found|: GEGL-gegl-operation.c'
        )
        self._config()


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

        subtask_mod.Background(options.get_gimp(
            ).get_cmdline()).run(pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
