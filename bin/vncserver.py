#!/usr/bin/env python3
"""
Wrapper for 'vncserver' command
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_vncserver(self):
        """
        Return vncserver Command class object.
        """
        return self._vncserver

    def _config(self):
        if not os.path.isfile(
                os.path.join(os.environ['HOME'], '.vnc', 'passwd')):
            raise SystemExit(
                sys.argv[0] +
                ': ".vnc/passwd" does not exist. Run "vncpasswd".'
            )
        os.chdir(os.environ['HOME'])
        xstartup = os.path.join(os.environ['HOME'], '.vnc', 'xstartup')
        if not os.path.isfile(xstartup):
            answer = input(
                'Would you like to use GNOME(g), KDE(k) or XFCE(x)? ')
            try:
                with open(xstartup, 'w', newline='\n') as ofile:
                    print('#!/bin/sh', file=ofile)
                    if answer[0].lower() == 'g':
                        print('unset DBUS_SESSION_BUS_ADDRESS', file=ofile)
                        print('unset SESSION_MANAGER', file=ofile)
                        print(
                            'if [ -x /usr/bin/gnome-session-fallback ]',
                            file=ofile
                        )
                        print('then', file=ofile)
                        print(
                            '    /usr/bin/gnome-session-fallback &',
                            file=ofile
                        )
                        print('elif [ -x /usr/bin/gnome-session ]', file=ofile)
                        print('then', file=ofile)
                        print('    /usr/bin/gnome-session &', file=ofile)
                        print('else', file=ofile)
                        print('    gnome &', file=ofile)
                        print('fi', file=ofile)
                    elif answer[0].lower() == 'k':
                        print('SESSION_MANAGER=', file=ofile)
                        print('startkde &', file=ofile)
                    elif answer[0].lower() == 'x':
                        print(
                            'unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS',
                            file=ofile
                        )
                        print('startxfce4 &', file=ofile)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create ".vnc/xstartup" file.')
            os.chmod(xstartup, int('755', 8) & ~self._umask)
        directory = os.path.dirname(self._vncserver.get_file())
        if (
                'PATH' in os.environ and
                directory not in os.environ['PATH'].split(os.pathsep)
        ):
            os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']

    def parse(self, args):
        """
        Parse arguments
        """
        self._vncserver = command_mod.Command(
            'vncserver',
            pathextra=['/usr/bin'],
            errors='stop'
        )
        self._vncserver.set_args([
            '-geometry',
            '1024x768',
            '-depth',
            '24',
            '-alwaysshared'
        ] + args[1:])
        self._umask = os.umask(int('077', 8))
        os.umask(self._umask)
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

        subtask_mod.Exec(options.get_vncserver().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
