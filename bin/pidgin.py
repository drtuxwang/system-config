#!/usr/bin/env python3
"""
Wrapper for "pidgin" command
"""

import glob
import os
import re
import shutil
import signal
import sys

import command_mod
import subtask_mod


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
    def _config():
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, '.purple')
        configfile = os.path.join(configdir, 'prefs.xml')
        try:
            with open(configfile, errors='replace') as ifile:
                try:
                    with open(
                            configfile + '.part',
                            'w',
                            newline='\n'
                    ) as ofile:
                        # Disable logging of chats
                        islog = re.compile('log_.*type="bool"')
                        for line in ifile:
                            if islog.search(line):
                                line = line.rstrip().replace('1', '0')
                            print(line, file=ofile)
                except OSError:
                    return
        except OSError:
            return
        try:
            shutil.move(configfile + '.part', configfile)
        except OSError:
            pass

    def run(self):
        """
        Start program
        """
        pidgin = command_mod.Command('pidgin', errors='stop')
        pidgin.set_args(sys.argv[1:])
        self._config()

        subtask_mod.Background(pidgin.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
