#!/usr/bin/env python3
"""
VMware Player launcher
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._vmplayer = syslib.Command("vmplayer")
        self._vmplayer.setArgs(args[1:])
        self._filter = ": Gtk-WARNING |: g_bookmark_file_get_size|^Fontconfig"
        self._config()


    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter


    def getVmplayer(self):
        """
        Return vmplayer Command class object.
        """
        return self._vmplayer


    def _config(self):
        if "HOME" in os.environ.keys():
            configfile = os.path.join(os.environ["HOME"], ".vmware", "config")
            if os.path.isfile(configfile):
                try:
                    with open(configfile, errors="replace") as ifile:
                        configdata = ifile.readlines()
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + configfile +
                                     '" configuration file.')
                if "xkeymap.nokeycodeMap = true\n" in configdata:
                    ifile.close()
                    return
                try:
                    ofile = open(configfile, "ab")
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot modify "' + configfile +
                                     '" configuration file.')
            else:
                configdir = os.path.dirname(configfile)
                if not os.path.isdir(configdir):
                    try:
                        os.mkdir(configdir)
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + configdir +
                                         '" directory.')
                try:
                    ofile = open(configfile, "w", newline="\n")
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + configfile +
                                     '" configuration file.')
            # Workaround VMWare Player 2.5 keymap bug
            print("xkeymap.nokeycodeMap = true")
            ofile.close()


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getVmplayer().run(filter=options.getFilter(), mode="background")
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
