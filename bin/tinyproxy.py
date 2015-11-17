#!/usr/bin/env python3
"""
Wrapper for 'tinyproxy' command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._tinyproxy = syslib.Command('tinyproxy')
        if len(args) > 1:
            self._tinyproxy.setArgs(args[1:])
        elif syslib.info.getUsername() != 'root':
            if not os.path.isfile('tinyproxy.conf'):
                self._createConfig()
            self._tinyproxy.setArgs(['-d', '-c', 'tinyproxy.conf'])

    def getTinyproxy(self):
        """
        Return tinyproxy Command class object.
        """
        return self._tinyproxy

    def _createConfig(self):
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


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getTinyproxy().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
