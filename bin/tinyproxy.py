#!/usr/bin/env python3
"""
Wrapper for 'tinyproxy' command
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
        self._tinyproxy = syslib.Command('tinyproxy')
        if len(args) > 1:
            self._tinyproxy.set_args(args[1:])
        elif syslib.info.get_username() != 'root':
            if not os.path.isfile('tinyproxy.conf'):
                self._create_config()
            self._tinyproxy.set_args(['-d', '-c', 'tinyproxy.conf'])

    def get_tinyproxy(self):
        """
        Return tinyproxy Command class object.
        """
        return self._tinyproxy

    def _create_config(self):
        try:
            with open('tinyproxy.conf', 'w', newline='\n') as ofile:
                print('Port 8888', file=ofile)
                print('PidFile "tinyproxy.pid"', file=ofile)
                print('LogFile "tinyproxy.log"', file=ofile)
                print('#', file=ofile)
                print('##LogLevel Critical', file=ofile)
                print('##LogLevel Error', file=ofile)
                print('LogLevel Warning', file=ofile)
                print('##LogLevel Notice', file=ofile)
                print('##LogLevel Connect', file=ofile)
                print('##LogLevel Info', file=ofile)
                print('#', file=ofile)
                print('ViaProxyName "tinyproxy"', file=ofile)
                print('Timeout 600', file=ofile)
                print('MaxClients 100', file=ofile)
                print('MinSpareServers 5', file=ofile)
                print('MaxSpareServers 20', file=ofile)
                print('StartServers 10', file=ofile)
                print('MaxRequestsPerChild 0', file=ofile)
                print('#', file=ofile)
                print('# SSL', file=ofile)
                print('ConnectPort 443', file=ofile)
                print('ConnectPort 563', file=ofile)
                print('#', file=ofile)
                print('# Restrict clients', file=ofile)
                print('##Allow 127.0.0.1', file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "tinyproxy.conf" configuration file.')


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
            options.get_tinyproxy().run(mode='exec')
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
