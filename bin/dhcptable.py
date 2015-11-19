#!/usr/bin/env python3
"""
Detect DHCP hosts on 192.168.1.0 subnet
"""

import glob
import os
import re
import signal
import sys
import threading
import time

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options:

    def __init__(self, args):
        self._arping = syslib.Command('arping', pathextra=['/sbin'])
        self._detect()

    def _detect(self):
        self._myip = '127.0.0.1'
        self._mymac = '00:00:00:00:00:00'
        self._subnet = '127.0.0'
        if syslib.info.getSystem() == 'linux':
            os.environ['LANG'] = 'en_GB'
            ifconfig = syslib.Command(file='/sbin/ifconfig')
            ifconfig.run(mode='batch')
            for line in ifconfig.getOutput(' HWaddr | inet addr[a-z]*:'):
                if ' HWaddr ' in line:
                    self._arping.setFlags(['-I', line.split()[0]])
                    self._mymac = line.split()[-1]
                else:
                    myip = line.split(':')[1].split()[0]
                    if myip not in ('', '127.0.0.1'):
                        break
        elif syslib.info.getSystem() == 'sunos':
            ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
            ifconfig.run(filter='\tinet [^ ]+ netmask', mode='batch')
            for line in ifconfig.getOutput():
                myip = line.split()[1]
                if myip not in ('', '127.0.0.1'):
                    break
        self._myip = myip
        self._subnet = self._myip.rsplit('.', 1)[0]

    def getArping(self):
        """
        Return arping Command class object.
        """
        return self._arping

    def getMyip(self):
        """
        Return my IP address.
        """
        return self._myip

    def getMymac(self):
        """
        Return my MAC address.
        """
        return self._mymac

    def getSubnet(self):
        """
        Return subnet.
        """
        return self._subnet


class ScanHost(threading.Thread):

    def __init__(self, options, ip):
        self._options = options
        threading.Thread.__init__(self)
        self._ip = ip
        self._output = ''

    def getIp(self):
        return self._ip

    def getOutput(self):
        return self._output

    def run(self):
        self._options.getArping().setArgs(['-c', '1', self._ip])
        self._child = self._options.getArping().run(mode='child', error2output=True)
        while True:
            byte = self._child.stdout.read(1)
            if not byte:
                break
            self._output += byte.decode('utf-8', 'replace')

    def kill(self):
        if self._child:
            self._child.kill()
            self._child = None


class ScanLan:

    def __init__(self, options):
        self._timeLimit = 1

        self._options = options
        self._avahiRdns = syslib.Command('avahi-resolve-address', check=False)
        self._threads = []

    def _detect(self):
        for host in range(1, 255):
            ip = self._options.getSubnet() + '.' + str(host)
            thread = ScanHost(self._options, ip)
            thread.start()
            self._threads.append(thread)

    def _output(self):
        for thread in self._threads:
            ip = thread.getIp()
            if ip == self._options.getMyip():
                print('{0:>11s} [{1:s}]  0.000ms  {2:s}'.format(
                    ip, self._options.getMymac(), self._reverseDNS(ip)))
            else:
                for line in thread.getOutput().split('\n'):
                    if line.startswith('Unicast reply from ' + ip):
                        mac, ping = line.split()[4:6]
                        print('{0:>11s} {1:s}  {2:s}  {3:s}'.format(
                            ip, mac, ping, self._reverseDNS(ip)))
                        break

        for thread in self._threads:
            thread.kill()

    def _reverseDNS(self, ip):
        if self._avahiRdns.isFound():
            self._avahiRdns.setArgs([ip])
            self._avahiRdns.run(mode='batch')
            if self._avahiRdns.hasOutput():
                return self._avahiRdns.getOutput()[0].split()[-1]
        return 'Unknown'

    def run(self):
        self._detect()
        time.sleep(self._timeLimit)
        self._output()


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            ScanLan(options).run()
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
