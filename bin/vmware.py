#!/usr/bin/env python3
"""
VMware Player launcher
"""

import glob
import os
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
        self._vmplayer = syslib.Command('vmplayer')
        self._vmplayer.set_args(args[1:])
        self._filter = ': Gtk-WARNING |: g_bookmark_file_get_size|^Fontconfig'
        self._config()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_vmplayer(self):
        """
        Return vmplayer Command class object.
        """
        return self._vmplayer

    def _config(self):
        if 'HOME' in os.environ:
            configfile = os.path.join(os.environ['HOME'], '.vmware', 'config')
            if os.path.isfile(configfile):
                try:
                    with open(configfile, errors='replace') as ifile:
                        configdata = ifile.readlines()
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + configfile + '" configuration file.')
                if 'xkeymap.nokeycodeMap = true\n' in configdata:
                    ifile.close()
                    return
                try:
                    ofile = open(configfile, 'ab')
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot modify "' + configfile + '" configuration file.')
            else:
                configdir = os.path.dirname(configfile)
                if not os.path.isdir(configdir):
                    try:
                        os.mkdir(configdir)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + configdir + '" directory.')
                try:
                    ofile = open(configfile, 'w', newline='\n')
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + configfile + '" configuration file.')
            # Workaround VMWare Player 2.5 keymap bug
            print('xkeymap.nokeycodeMap = true')
            ofile.close()


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            options.get_vmplayer().run(filter=options.get_filter(), mode='background')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
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
