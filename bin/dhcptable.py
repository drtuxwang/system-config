#!/usr/bin/env python3
"""
Detect DHCP hosts on 192.168.1.0 subnet
"""

import os
import signal
import sys
import threading
import time

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._arping = syslib.Command('arping', pathextra=['/sbin'])
        self._detect()

    def _detect(self):
        self._myip = '127.0.0.1'
        self._mymac = '00:00:00:00:00:00'
        self._subnet = '127.0.0'
        if syslib.info.get_system() == 'linux':
            os.environ['LANG'] = 'en_GB'
            ifconfig = syslib.Command(file='/sbin/ifconfig')
            ifconfig.run(mode='batch')
            for line in ifconfig.get_output(' HWaddr | inet addr[a-z]*:'):
                if ' HWaddr ' in line:
                    self._arping.set_flags(['-I', line.split()[0]])
                    self._mymac = line.split()[-1]
                else:
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
        self._myip = myip
        self._subnet = self._myip.rsplit('.', 1)[0]

    def get_arping(self):
        """
        Return arping Command class object.
        """
        return self._arping

    def get_myip(self):
        """
        Return my IP address.
        """
        return self._myip

    def get_mymac(self):
        """
        Return my MAC address.
        """
        return self._mymac

    def get_subnet(self):
        """
        Return subnet.
        """
        return self._subnet


class ScanHost(threading.Thread):
    """
    Scan host class
    """

    def __init__(self, options, ip):
        self._options = options
        threading.Thread.__init__(self)
        self._ip = ip
        self._child = None
        self._output = ''

    def get_ip(self):
        """
        Return IP address
        """
        return self._ip

    def get_output(self):
        """
        Return output
        """
        return self._output

    def run(self):
        """
        Start thread
        """
        self._options.get_arping().set_args(['-c', '1', self._ip])
        self._child = self._options.get_arping().run(mode='child', error2output=True)
        while True:
            byte = self._child.stdout.read(1)
            if not byte:
                break
            self._output += byte.decode('utf-8', 'replace')

    def kill(self):
        """
        Kill thread
        """
        if self._child:
            self._child.kill()
            self._child = None


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
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _detect(self):
        for host in range(1, 255):
            ip_address = self._options.get_subnet() + '.' + str(host)
            thread = ScanHost(self._options, ip_address)
            thread.start()
            self._threads.append(thread)

    def _output(self):
        for thread in self._threads:
            ip_address = thread.get_ip()
            if ip_address == self._options.get_myip():
                print('{0:>11s} [{1:s}]  0.000ms  {2:s}'.format(
                    ip_address, self._options.get_mymac(), self._reverse_dns(ip_address)))
            else:
                for line in thread.get_output().split('\n'):
                    if line.startswith('Unicast reply from ' + ip_address):
                        mac, ping = line.split()[4:6]
                        print('{0:>11s} {1:s}  {2:s}  {3:s}'.format(
                            ip_address, mac, ping, self._reverse_dns(ip_address)))
                        break

        for thread in self._threads:
            thread.kill()

    def _reverse_dns(self, ip_address):
        if self._avahi_rdns.is_found():
            self._avahi_rdns.set_args([ip_address])
            self._avahi_rdns.run(mode='batch')
            if self._avahi_rdns.has_output():
                return self._avahi_rdns.get_output()[0].split()[-1]
        return 'Unknown'

    def run(self):
        """
        Start program
        """
        options = Options()

        self._time_limit = 1

        self._options = options
        self._avahi_rdns = syslib.Command('avahi-resolve-address', check=False)
        self._threads = []

        self._detect()
        time.sleep(self._time_limit)
        self._output()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
