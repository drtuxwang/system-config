#!/usr/bin/env python3
"""
Run command on a subnet in parallel.
"""

import argparse
import glob
import os
import re
import signal
import sys
import threading
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_command_line(self):
        """
        Return command line.
        """
        return self._args.command + self._command_args

    def get_ssh(self):
        """
        Return ssh Command class object.
        """
        return self._ssh

    def get_subnet(self):
        """
        Return subnet.
        """
        return self._subnet

    @staticmethod
    def _getmyip():
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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Run command on a subnet in parallel.\n')

        parser.add_argument('-subnet', nargs=1, metavar='netmask',
                            help='Select netmask in the format "192.168.149.0".')

        parser.add_argument('command', nargs=1, help='Command to run on all systems.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        my_args = []
        while len(args):
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-subnet' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._command_args = args[1:]

        issubnet = re.compile(r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]0$')
        if self._args.subnet and issubnet.match(self._args.subnet[0]):
            self._subnet = self._args.subnet[0]
        else:
            myip = self._getmyip()
            if not myip:
                raise SystemExit(sys.argv[0] + ": Cannot determine subnet configuration.")
            self._subnet = myip.rsplit('.', 1)[0]

        self._ssh = syslib.Command('ssh')
        self._ssh.set_flags(['-o', 'StrictHostKeyChecking=no', '-o',
                             'UserKnownHostsFile=/dev/null', '-o', 'BatchMode=yes'])


class Remote(threading.Thread):
    """
    Remote class
    """

    def __init__(self, options, ip):
        self._options = options
        threading.Thread.__init__(self)
        self._ip = ip
        self._output = ''
        self._child = None

    def get_output(self):
        """
        Get output
        """
        return self._output

    def run(self):
        """
        Run command
        """
        ssh = self._options.get_ssh()
        ssh.set_args([self._ip, 'echo "=== ' + self._ip + ': "`uname -s -n`" ==="; ' + ssh.args2cmd(
            self._options.get_command_line())])

        self._child = ssh.run(mode='child', error2output=True)
        self._child.stdin.close()
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _allreduce(self):
        print('\rAllreduce from subnet "' + self._options.get_subnet() + '.0"...')
        obytes = 0
        same = 0
        alive = True

        while alive:
            nbytes = 0
            alive = False
            for thread in self._threads:
                nbytes += len(thread.get_output())
                if thread.is_alive():
                    alive = True
            sys.stdout.write('\r  -> Received ' + str(nbytes) + ' bytes...')
            sys.stdout.flush()
            if nbytes == obytes:
                same += 1
                if same > self._wait_max:
                    break
            else:
                same = 0
                obytes = nbytes
            time.sleep(self._wait_time)
        print()

    def _bcast(self):
        print('Bcast to subnet "' + self._options.get_subnet() + '.0"...')
        for host in range(1, 255):
            ip_address = self._options.get_subnet() + '.' + str(host)
            sys.stdout.write('\r  -> ' + str(ip_address) + '...')
            sys.stdout.flush()
            thread = Remote(self._options, ip_address)
            thread.start()
            self._threads.append(thread)

    def _output(self):
        iserror = re.compile('Command not supported|Network is unreachable|No route to host|'
                             'Permission denied.|protocol failure in circuit setup', re.IGNORECASE)

        for thread in self._threads:
            output = thread.get_output()
            if output and not iserror.search(output):
                print(thread.get_output().rstrip('\r\n'))

        for thread in self._threads:
            thread.kill()

    def run(self):
        """
        Start program
        """
        self._options = Options()
        self._wait_max = 64
        self._wait_time = 0.1

        self._threads = []
        self._bcast()
        self._allreduce()
        self._output()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
