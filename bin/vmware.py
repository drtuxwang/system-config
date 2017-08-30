#!/usr/bin/env python3
"""
VMware Player launcher
"""

import glob
import os
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

    def get_vmplayer(self):
        """
        Return vmplayer Command class object.
        """
        return self._vmplayer

    @staticmethod
    def _config():
        home = os.environ.get('HOME', '')
        configfile = os.path.join(home, '.vmware', 'config')
        if os.path.isfile(configfile):
            try:
                with open(configfile, errors='replace') as ifile:
                    configdata = ifile.readlines()
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + configfile +
                    '" configuration file.'
                )
            if 'xkeymap.nokeycodeMap = true\n' in configdata:
                ifile.close()
                return
            try:
                ofile = open(configfile, 'ab')
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot modify "' + configfile +
                    '" configuration file.'
                )
        else:
            configdir = os.path.dirname(configfile)
            if not os.path.isdir(configdir):
                try:
                    os.mkdir(configdir)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + configdir +
                        '" directory.'
                    )
            try:
                ofile = open(configfile, 'w', newline='\n')
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + configfile +
                    '" configuration file.'
                )
        # Workaround VMWare Player 2.5 keymap bug
        print("xkeymap.nokeycodeMap = true")
        ofile.close()

    def parse(self, args):
        """
        Parse arguments
        """
        self._vmplayer = command_mod.Command('vmplayer', errors='stop')
        self._vmplayer.set_args(args[1:])
        self._pattern = ': Gtk-WARNING |: g_bookmark_file_get_size|^Fontconfig'
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

        subtask_mod.Background(options.get_vmplayer().get_cmdline()).run(
            pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
