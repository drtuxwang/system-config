#!/usr/bin/env python3
"""
Detect DHCP hosts on /24 subnets
"""

import os
import signal
import sys
import threading
import time

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
        self._arping = command_mod.Command(
            'arping',
            pathextra=['/sbin'],
            errors='stop'
        )
        self._detect()

    def _detect(self):
        self._networks = []
        mydev = None
        myip = None
        mymac = '00:00:00:00:00:00'
        if os.name == 'posix':
            osname = os.uname()[0]
            if osname == 'Linux':
                os.environ['LANG'] = 'en_GB'
                ifconfig = command_mod.CommandFile('/sbin/ifconfig')
                task = subtask_mod.Batch(ifconfig.get_cmdline())
                task.run()
                for line in task.get_output(' HWaddr | inet addr[a-z]*:'):
                    if ' HWaddr ' in line:
                        mydev = line.split()[0]
                        mymac = line.split()[-1]
                    else:
                        myip = line.split(':')[1].split()[0]
                        if myip not in ('', '127.0.0.1'):
                            self._networks.append([mydev, myip, mymac])

    def get_arping(self):
        """
        Return arping Command class object.
        """
        return self._arping

    def get_networks(self):
        """
        Return networks in (ip, mac) format.
        """
        return self._networks


class ScanHost(threading.Thread):
    """
    Scan host class
    """

    def __init__(self, arping, network, ip):
        self._cmdline = arping.get_cmdline() + ['-I', network[0]]
        self._network = network
        self._ip = ip
        threading.Thread.__init__(self, daemon=True)
        self._child = None
        self._output = ''

    def get_network(self):
        """
        Return network as (mynet, myip, mymac).
        """
        return self._network

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
        self._child = subtask_mod.Child(
            self._cmdline + ['-c', '3', self._ip]).run(error2output=True)
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
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _detect(self):
        arping = self._options.get_arping()
        for network in self._options.get_networks():
            subnet = network[1].rsplit('.', 1)[0]
            for ip_address in (subnet + '.' + str(x) for x in range(1, 255)):
                thread = ScanHost(arping, network, ip_address)
                thread.start()
                self._threads.append(thread)

    def _output(self):
        for thread in self._threads:
            network = thread.get_network()
            ip_address = thread.get_ip()
            if ip_address == network[1]:
                print("{0:15s} [{1:s}]   0.000ms  {2:s}".format(
                    network[1], network[2], self._reverse_dns(ip_address)))
            else:
                for line in thread.get_output().split('\n'):
                    if line.startswith('Unicast reply from ' + ip_address):
                        mac, ping = line.split()[4:6]
                        print("{0:15s} {1:s} {2:>9s}  {3:s}".format(
                            ip_address,
                            mac,
                            ping,
                            self._reverse_dns(ip_address)
                        ))
                        break

        for thread in self._threads:
            thread.kill()

    def _reverse_dns(self, ip_address):
        if self._avahi_rdns.is_found():
            self._avahi_rdns.set_args([ip_address])
            task = subtask_mod.Batch(self._avahi_rdns.get_cmdline())
            task.run()
            if task.has_output():
                return task.get_output()[0].split()[-1]
        return 'Unknown'

    def run(self):
        """
        Start program
        """
        options = Options()

        self._time_limit = 1

        self._options = options
        self._avahi_rdns = command_mod.Command(
            'avahi-resolve-address',
            errors='ignore'
        )
        self._threads = []

        self._detect()
        time.sleep(self._time_limit)
        self._output()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
