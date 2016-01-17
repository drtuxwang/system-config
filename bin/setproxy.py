#!/usr/bin/env python3
"""
Determine proxy server address
"""

import glob
import os
import re
import signal
import sys
import urllib.request

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Proxy(object):
    """
    Proxy class
    """

    def __init__(self):
        myip = self._getmyip()
        myproxy = ''
        if 'http_proxy' in os.environ:
            if os.environ['http_proxy'].startswith('http://'):
                myproxy = os.environ['http_proxy'][7:]
            del(os.environ['http_proxy'])
        if re.match('^192.168.14[89][.][0-9]+$', myip):
            try:
                with urllib.request.urlopen('http://intranet/proxy.pac') as ifile:
                    isMatch = re.compile('^return "PROXY ')
                    for line in ifile:
                        if isMatch.match(str(line)):
                            myproxy = line.split('"')[1][6:]
                            break
            except IOError:
                pass
        print(myproxy)

    def _getmyip(self):
        myip = ''
        if syslib.info.get_system() == 'linux':
            os.environ['LANG'] = 'en_GB'
            ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
            ifconfig.run(filter=' inet addr[a-z]*:', mode='batch')
            for line in ifconfig.get_output():
                myip = line.split(':')[1].split()[0]
                if myip not in ('', '127.0.0.1'):
                    break
        elif syslib.info.get_system() == 'sunos':
            ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
            ifconfig.run(filter='\tinet [^ ]+ netmask', mode='batch')
            for line in ifconfig.get_output():
                myip = line.split()[1]
                if myip not in ('', '127.0.0.1'):
                    break
        return myip


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            Proxy()
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
